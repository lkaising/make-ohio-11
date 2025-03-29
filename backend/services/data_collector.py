import os
import json
import time
import requests
from typing import List, Dict, Any, Optional
import sys

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GOOGLE_PLACES_API_KEY, DATA_DIR, MAX_RESTAURANTS_PER_ZIP

class GooglePlacesCollector:
    """
    Service to collect restaurant data using Google Places API,
    optimized to gather only the essential fields needed for restaurant recommendations
    """
    
    def __init__(self):
        self.api_key = GOOGLE_PLACES_API_KEY
        if not self.api_key:
            raise ValueError("Google Places API key is not set in environment variables")
        
        # Ensure data directory exists
        os.makedirs(DATA_DIR, exist_ok=True)
        
        # Load Ohio zip codes
        self.ohio_zipcodes = self._load_zipcodes()
    
    def _load_zipcodes(self) -> Dict[str, List[str]]:
        """Load Ohio zip codes from JSON file"""
        zipcode_path = os.path.join(DATA_DIR, "ohio_zipcodes.json")
        if os.path.exists(zipcode_path):
            with open(zipcode_path, 'r') as f:
                return json.load(f)
        else:
            raise FileNotFoundError(f"Ohio zip codes file not found at {zipcode_path}")
    
    def _search_restaurants_by_zipcode(self, zipcode: str) -> List[Dict[str, Any]]:
        """
        Search for restaurants in a specific zip code using Google Places API
        """
        base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        
        # Search for restaurants in this zip code
        params = {
            "query": f"restaurants in {zipcode} ohio",
            "type": "restaurant",
            "key": self.api_key
        }
        
        results = []
        next_page_token = None
        
        # Collect up to MAX_RESTAURANTS_PER_ZIP establishments or max 3 pages
        page_count = 0
        max_pages = 20
        
        while page_count < max_pages and len(results) < MAX_RESTAURANTS_PER_ZIP:
            # If we have a page token from a previous request, use it
            if next_page_token and page_count > 0:
                # Google requires a short delay before using the next_page_token
                time.sleep(2)
                params = {"pagetoken": next_page_token, "key": self.api_key}
            
            response = requests.get(base_url, params=params)
            data = response.json()
            
            if response.status_code != 200 or "error_message" in data:
                error_msg = data.get("error_message", "Unknown error")
                print(f"Error searching restaurants in {zipcode}: {error_msg}")
                break
            
            # Add results to our list
            if "results" in data:
                results.extend(data["results"])
                print(f"Found {len(data['results'])} restaurants in {zipcode} (page {page_count + 1})")
            
            # Get next page token if available
            next_page_token = data.get("next_page_token")
            page_count += 1
            
            # If we've collected enough restaurants, stop
            if len(results) >= MAX_RESTAURANTS_PER_ZIP:
                results = results[:MAX_RESTAURANTS_PER_ZIP]
                break
        
        return results
    
    def _get_place_details(self, place_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a place using its place_id
        Optimized to only request the essential fields needed
        """
        base_url = "https://maps.googleapis.com/maps/api/place/details/json"
        
        # Request only the fields we need for the recommendation system
        params = {
            "place_id": place_id,
            "fields": "name,place_id,formatted_address,rating,user_ratings_total,price_level,types,reviews",
            "key": self.api_key
        }
        
        response = requests.get(base_url, params=params)
        data = response.json()
        
        if response.status_code != 200 or "error_message" in data:
            error_msg = data.get("error_message", "Unknown error")
            print(f"Error getting details for place {place_id}: {error_msg}")
            return {}
        
        return data.get("result", {})
    
    def collect_restaurants(self, cities: Optional[List[str]] = None, zipcodes: Optional[List[str]] = None) -> None:
        """
        Collect restaurant data by cities or zipcodes
        
        Args:
            cities: List of city names to collect data for
            zipcodes: List of specific zip codes to collect data for
        """
        all_restaurants = []
        
        # Process by zipcodes if provided
        if zipcodes:
            print(f"Collecting restaurant data for specific zipcodes: {', '.join(zipcodes)}")
            # Find city for each zipcode if possible
            zipcode_to_city = {}
            for city, city_zipcodes in self.ohio_zipcodes.items():
                for zipcode in city_zipcodes:
                    zipcode_to_city[zipcode] = city
            
            self._process_zipcodes(zipcodes, None, all_restaurants, zipcode_to_city)
        # Otherwise process by cities
        else:
            cities_to_process = cities if cities else list(self.ohio_zipcodes.keys())
            print(f"Collecting restaurant data for cities: {', '.join(cities_to_process)}")
            
            for city in cities_to_process:
                if city not in self.ohio_zipcodes:
                    print(f"City {city} not found in Ohio zip codes list")
                    continue
                    
                print(f"Collecting restaurants for {city}...")
                zipcodes = self.ohio_zipcodes[city]
                
                # Process each zipcode in this city
                self._process_zipcodes(zipcodes, city, all_restaurants)
        
        print(f"Collected data for {len(all_restaurants)} restaurants")
    
    # Compatibility methods that use the new unified collect_restaurants method
    def collect_all_restaurants(self, cities: Optional[List[str]] = None) -> None:
        """Collect restaurant data for all Ohio zip codes or specified cities"""
        self.collect_restaurants(cities=cities)
    
    def collect_by_zipcodes(self, zipcodes: List[str]) -> None:
        """Collect restaurant data for specific zip codes"""
        self.collect_restaurants(zipcodes=zipcodes)
    
    def _process_zipcodes(self, zipcodes: List[str], default_city: Optional[str] = None, 
                          all_restaurants: Optional[List[Dict[str, Any]]] = None,
                          zipcode_to_city: Optional[Dict[str, str]] = None) -> None:
        """
        Helper method to process a list of zipcodes and collect restaurant data
        
        Args:
            zipcodes: List of zip codes to process
            default_city: Default city name to assign (used when collecting by city)
            all_restaurants: List to append restaurant data to
            zipcode_to_city: Optional mapping of zipcode to city name (used when collecting by zipcode)
        """
        if all_restaurants is None:
            all_restaurants = []
            
        for zipcode in zipcodes:
            print(f"Processing zip code: {zipcode}")
            restaurants = self._search_restaurants_by_zipcode(zipcode)
            
            # Determine city for this zipcode
            city = default_city
            if city is None and zipcode_to_city and zipcode in zipcode_to_city:
                city = zipcode_to_city[zipcode]
            elif city is None:
                city = "unknown"  # Fallback if we can't determine the city
            
            # Get detailed information for each restaurant
            for restaurant in restaurants:
                place_id = restaurant.get("place_id")
                if place_id:
                    details = self._get_place_details(place_id)
                    if details:
                        # Add city and zip code info
                        details["city"] = city
                        details["zipcode"] = zipcode
                        all_restaurants.append(details)
            
            # Save intermediate results in case of failures
            self._save_restaurants(all_restaurants)
            
            # Respect API rate limits
            time.sleep(2)
    
    def _save_restaurants(self, restaurants: List[Dict[str, Any]]) -> None:
        """
        Save restaurant data to JSON file
        Formats data to include only essential fields needed for recommendations
        """
        output_path = os.path.join(DATA_DIR, "restaurants.json")
        
        # First, load existing restaurants to avoid duplicates when appending new data
        existing_restaurants = []
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            try:
                with open(output_path, 'r', encoding='utf-8') as f:
                    existing_restaurants = json.load(f)
                print(f"Loaded {len(existing_restaurants)} existing restaurants")
            except json.JSONDecodeError:
                print("Warning: Existing restaurant data file is corrupted. Starting with empty dataset.")
        
        # Track existing place_ids to avoid duplicates
        existing_place_ids = {r.get("place_id") for r in existing_restaurants}
        
        # Convert to a consistent structure with only the fields we need
        formatted_restaurants = existing_restaurants.copy()
        new_count = 0
        
        for restaurant in restaurants:
            place_id = restaurant.get("place_id", "")
            
            # Skip if this restaurant is already in our dataset
            if place_id in existing_place_ids:
                continue
                
            existing_place_ids.add(place_id)
            new_count += 1
            
            # Extract only the essential fields we need
            formatted = {
                "place_id": place_id,
                "name": restaurant.get("name", ""),
                "address": restaurant.get("formatted_address", ""),
                "city": restaurant.get("city", ""),
                "zipcode": restaurant.get("zipcode", ""),
                "rating": restaurant.get("rating", 0),
                "user_ratings_total": restaurant.get("user_ratings_total", 0),
                "price_level": restaurant.get("price_level", 0),
                "types": restaurant.get("types", []),
                "reviews": []
            }
            
            # Add reviews if available - only keep author_name, rating, and text
            if "reviews" in restaurant:
                for review in restaurant["reviews"]:
                    formatted["reviews"].append({
                        "author_name": review.get("author_name", ""),
                        "rating": review.get("rating", 0),
                        "text": review.get("text", ""),
                        "time": review.get("time", 0)
                    })
            
            formatted_restaurants.append(formatted)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(formatted_restaurants, f, ensure_ascii=False, indent=2)
        
        print(f"Saved {len(formatted_restaurants)} restaurants to {output_path} ({new_count} new)")
        print("Run 'python app.py --process' next to process this data for LLM recommendations")