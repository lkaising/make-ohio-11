import os
import json
from typing import List, Dict, Any
import sys

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATA_DIR

class DataProcessor:
    """
    Utility class for processing and cleaning restaurant data
    """
    
    def __init__(self):
        self.data_dir = DATA_DIR
        self.restaurants_path = os.path.join(self.data_dir, "restaurants.json")
    
    def load_restaurants(self) -> List[Dict[str, Any]]:
        """Load restaurants from the JSON file"""
        if not os.path.exists(self.restaurants_path):
            print(f"Restaurant data not found at {self.restaurants_path}")
            return []
        
        with open(self.restaurants_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def clean_data(self) -> None:
        """Clean the restaurant data to ensure consistency and remove duplicates"""
        restaurants = self.load_restaurants()
        
        if not restaurants:
            return
        
        cleaned = []
        seen_place_ids = set()
        
        for restaurant in restaurants:
            place_id = restaurant.get("place_id")
            
            # Skip duplicates
            if place_id in seen_place_ids:
                continue
                
            seen_place_ids.add(place_id)
            
            # Ensure all fields exist
            restaurant = {
                "place_id": restaurant.get("place_id", ""),
                "name": restaurant.get("name", ""),
                "address": restaurant.get("address", ""),
                "city": restaurant.get("city", ""),
                "zipcode": restaurant.get("zipcode", ""),
                "lat": restaurant.get("lat", 0),
                "lng": restaurant.get("lng", 0),
                "rating": restaurant.get("rating", 0),
                "user_ratings_total": restaurant.get("user_ratings_total", 0),
                "price_level": restaurant.get("price_level", 0),
                "website": restaurant.get("website", ""),
                "phone": restaurant.get("phone", ""),
                "types": restaurant.get("types", []),
                "reviews": restaurant.get("reviews", [])
            }
            
            # Format reviews consistently
            formatted_reviews = []
            for review in restaurant["reviews"]:
                formatted_reviews.append({
                    "author_name": review.get("author_name", ""),
                    "rating": review.get("rating", 0),
                    "text": review.get("text", ""),
                    "time": review.get("time", 0)
                })
            
            restaurant["reviews"] = formatted_reviews
            
            # Extract cuisine types from the 'types' field
            cuisine_types = set()
            for type_str in restaurant["types"]:
                if type_str not in ["restaurant", "food", "point_of_interest", "establishment"]:
                    cuisine_types.add(type_str)
            
            restaurant["cuisine_types"] = list(cuisine_types)
            
            cleaned.append(restaurant)
        
        # Save the cleaned data
        with open(self.restaurants_path, 'w', encoding='utf-8') as f:
            json.dump(cleaned, f, ensure_ascii=False, indent=2)
        
        print(f"Cleaned data for {len(cleaned)} restaurants")
    
    def generate_cuisine_stats(self) -> Dict[str, int]:
        """Generate statistics about cuisine types"""
        restaurants = self.load_restaurants()
        
        cuisine_counts = {}
        
        for restaurant in restaurants:
            for cuisine in restaurant.get("cuisine_types", []):
                if cuisine in cuisine_counts:
                    cuisine_counts[cuisine] += 1
                else:
                    cuisine_counts[cuisine] = 1
        
        # Sort by count
        sorted_cuisines = {k: v for k, v in sorted(cuisine_counts.items(), key=lambda item: item[1], reverse=True)}
        
        return sorted_cuisines
    
    def generate_price_stats(self) -> Dict[str, int]:
        """Generate statistics about price levels"""
        restaurants = self.load_restaurants()
        
        price_counts = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
        price_labels = {0: "Unknown", 1: "$", 2: "$$", 3: "$$$", 4: "$$$$"}
        
        for restaurant in restaurants:
            price_level = restaurant.get("price_level", 0)
            price_counts[price_level] += 1
        
        # Convert to labels
        labeled_counts = {price_labels[k]: v for k, v in price_counts.items()}
        
        return labeled_counts