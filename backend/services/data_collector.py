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
    Service to collect restaurant data using Google Places API
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
        max_pages = 3
        
        while page_count < max_pages and (next_page_token is None or page_count > 0) and len(results) < MAX_RESTAURANTS_PER_ZIP:
            # If we have a page token from a previous request, use it
            if next_page_token:
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
        """
        base_url = "https://maps.googleapis.com/maps/api/place/details/json"
        
        params = {
            "place_id": place_id,
            "fields": "name,place_id,formatted_address,geometry,rating,user_ratings_total,price_level,website,formatted_phone_number,reviews,types",
            "key": self.api_key
        }
        
        response = requests.get(base_url, params=params)
        data = response.json()
        
        if response.status_code != 200 or "error_message" in data:
            error_msg = data.get("error_message", "Unknown error")
            print(f"Error getting details for place {place_id}: {error_msg}")
            return {}
        
        if "result" in data:
            return data["result"]
        return {}
    
    def collect_all_restaurants(self, cities: Optional[List[str]] = None) -> None:
        """
        Collect restaurant data for all Ohio zip codes or specified cities
        
        Args:
            cities: List of city names to collect data for. If None, collects for all cities.
        """
        all_restaurants = []
        
        # Process zip codes by city
        cities_to_process = cities if cities else list(self.ohio_zipcodes.keys())
        
        for city in cities_to_process:
            if city not in self.ohio_zipcodes:
                print(f"City {city} not found in Ohio zip codes list")
                continue
                
            print(f"Collecting restaurants for {city}...")
            zipcodes = self.ohio_zipcodes[city]
            
            for zipcode in zipcodes:
                print(f"Processing zip code: {zipcode}")
                restaurants = self._search_restaurants_by_zipcode(zipcode)
                
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
                time.sleep(1)
        
        print(f"Collected data for {len(all_restaurants)} restaurants")
    
    def _save_restaurants(self, restaurants: List[Dict[str, Any]]) -> None:
        """Save restaurant data to JSON file"""
        output_path = os.path.join(DATA_DIR, "restaurants.json")
        
        # Convert to a consistent structure
        formatted_restaurants = []
        
        for restaurant in restaurants:
            # Extract the most relevant fields
            formatted = {
                "place_id": restaurant.get("place_id", ""),
                "name": restaurant.get("name", ""),
                "address": restaurant.get("formatted_address", ""),
                "city": restaurant.get("city", ""),
                "zipcode": restaurant.get("zipcode", ""),
                "lat": restaurant.get("geometry", {}).get("location", {}).get("lat", 0),
                "lng": restaurant.get("geometry", {}).get("location", {}).get("lng", 0),
                "rating": restaurant.get("rating", 0),
                "user_ratings_total": restaurant.get("user_ratings_total", 0),
                "price_level": restaurant.get("price_level", 0),
                "website": restaurant.get("website", ""),
                "phone": restaurant.get("formatted_phone_number", ""),
                "types": restaurant.get("types", []),
                "reviews": []
            }
            
            # Add reviews if available
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
        
        print(f"Saved {len(formatted_restaurants)} restaurants to {output_path}")


class OutscraperCollector:
    """
    Alternative service to collect restaurant data using Outscraper API
    """
    def __init__(self):
        # This would be implemented similar to GooglePlacesCollector but using Outscraper API
        # Leaving this as a placeholder for now
        pass