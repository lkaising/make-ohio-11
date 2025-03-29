import os
import json
import re
from typing import List, Dict, Any
from collections import Counter
import sys

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATA_DIR

# Common food-related words to ignore when extracting dishes
COMMON_FOOD_WORDS = {
    "food", "meal", "lunch", "dinner", "breakfast", "appetizer", "entree", 
    "dessert", "drink", "beverage", "dish", "plate", "order", "menu", "restaurant",
    "delicious", "tasty", "yummy", "good", "great", "excellent", "amazing",
    "terrible", "bad", "awful", "okay", "decent", "fine", "average", "mediocre"
}

# Keywords for restaurant characteristics
DESCRIPTOR_PATTERNS = {
    "affordable": ["affordable", "cheap", "inexpensive", "budget", "low price", "good price", "good value", "value for money"],
    "expensive": ["expensive", "pricey", "high-end", "upscale", "fancy", "costly", "overpriced"],
    "family_friendly": ["family", "kid", "child", "family-friendly", "family friendly", "family oriented"],
    "quick_service": ["fast", "quick", "speedy", "rapid", "prompt", "efficient", "quick service"],
    "casual": ["casual", "relaxed", "laid-back", "informal", "chill", "cozy"],
    "fancy": ["fancy", "upscale", "elegant", "sophisticated", "classy", "high-end", "fine dining"],
    "late_night": ["late night", "late-night", "late", "24 hour", "24-hour", "all night", "all-night"],
    "romantic": ["romantic", "date", "intimate", "cozy", "quiet", "candle", "ambiance"],
    "takeout": ["takeout", "take-out", "take out", "to-go", "to go", "delivery", "pickup", "pick-up", "carry-out"],
    "healthy": ["healthy", "nutritious", "organic", "vegan", "vegetarian", "gluten-free", "gluten free", "plant-based"],
    "comfort_food": ["comfort", "comfort food", "homemade", "home-made", "hearty", "filling", "classic"],
    "authentic": ["authentic", "traditional", "genuine", "real", "original", "true", "legitimate"]
}

# Price level mapping
PRICE_MAPPING = {
    0: "Unknown",
    1: "$",
    2: "$$",
    3: "$$$",
    4: "$$$$"
}

# Enhanced cuisine type mapping (Google Place types to more specific cuisine categories)
CUISINE_MAPPING = {
    "bakery": "Bakery",
    "bar": "Bar/Pub",
    "cafe": "Café",
    "meal_takeaway": "Takeout",
    "meal_delivery": "Delivery",
    "restaurant": "Restaurant",
    "american_restaurant": "American",
    "bbq": "BBQ",
    "burger_restaurant": "Burgers",
    "chinese_restaurant": "Chinese",
    "fast_food_restaurant": "Fast Food",
    "french_restaurant": "French",
    "greek_restaurant": "Greek",
    "indian_restaurant": "Indian",
    "italian_restaurant": "Italian",
    "japanese_restaurant": "Japanese",
    "korean_restaurant": "Korean",
    "mexican_restaurant": "Mexican",
    "middle_eastern_restaurant": "Middle Eastern",
    "pizza_restaurant": "Pizza",
    "seafood_restaurant": "Seafood",
    "steak_house": "Steakhouse",
    "sushi_restaurant": "Sushi",
    "thai_restaurant": "Thai",
    "vegetarian_restaurant": "Vegetarian",
    "vietnamese_restaurant": "Vietnamese"
}

class DataProcessor:
    """
    Utility class for processing and cleaning restaurant data
    """
    
    def __init__(self):
        self.restaurants_path = os.path.join(DATA_DIR, "restaurants.json")
    
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
                if type_str in CUISINE_MAPPING:
                    cuisine_types.add(CUISINE_MAPPING[type_str])
                elif type_str not in ["restaurant", "food", "point_of_interest", "establishment"]:
                    # Convert snake_case to Title Case for readability
                    formatted_type = " ".join(word.capitalize() for word in type_str.split("_"))
                    cuisine_types.add(formatted_type)
            
            restaurant["cuisine_types"] = list(cuisine_types)
            
            # Format price level
            restaurant["price_display"] = PRICE_MAPPING.get(restaurant["price_level"], "Unknown")
            
            # Add enhanced data if reviews are available
            if restaurant["reviews"]:
                # Extract popular dishes, keywords, and create a summary
                restaurant["popular_dishes"] = self.extract_popular_dishes(restaurant["reviews"])
                restaurant["descriptors"] = self.extract_descriptors(restaurant["reviews"])
                restaurant["sentiment"] = self.calculate_sentiment(restaurant["reviews"])
                restaurant["profile"] = self.create_restaurant_profile(restaurant)
            else:
                restaurant["popular_dishes"] = []
                restaurant["descriptors"] = []
                restaurant["sentiment"] = "neutral"
                restaurant["profile"] = f"{restaurant['name']} is a restaurant in {restaurant['city']}."
            
            cleaned.append(restaurant)
        
        # Save the cleaned data
        with open(self.restaurants_path, 'w', encoding='utf-8') as f:
            json.dump(cleaned, f, ensure_ascii=False, indent=2)
        
        print(f"Cleaned and enhanced data for {len(cleaned)} restaurants")
    
    def extract_popular_dishes(self, reviews: List[Dict[str, Any]]) -> List[str]:
        """Extract potential popular dishes from reviews using capitalized phrases and frequency"""
        potential_dishes = []
        
        # Look for capitalized phrases which are often dishes
        for review in reviews:
            text = review.get("text", "")
            
            # Find capitalized words (likely to be dish names)
            capitalized_phrases = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', text)
            
            # Also try to find phrases that might be food items
            food_phrases = re.findall(r'\b(\w+\s+(?:burger|pizza|sandwich|salad|pasta|taco|burrito|chicken|steak|fish|soup|dessert)s?)\b', text.lower())
            
            # Add capitalized phrases that aren't common words
            for phrase in capitalized_phrases:
                if len(phrase) > 3 and phrase.lower() not in COMMON_FOOD_WORDS:
                    potential_dishes.append(phrase)
            
            # Add food phrases
            for phrase in food_phrases:
                if phrase not in potential_dishes:
                    # Capitalize first letter of each word for consistency
                    formatted_phrase = " ".join(word.capitalize() for word in phrase.split())
                    potential_dishes.append(formatted_phrase)
        
        # Count frequencies and return most common
        if potential_dishes:
            dish_counter = Counter(potential_dishes)
            return [dish for dish, count in dish_counter.most_common(10) if count > 1]
        
        return []
    
    def extract_descriptors(self, reviews: List[Dict[str, Any]]) -> List[str]:
        """Extract descriptive keywords from reviews"""
        descriptors = set()
        
        # Combine all review text
        all_text = " ".join([review.get("text", "").lower() for review in reviews])
        
        # Look for descriptor patterns
        for category, patterns in DESCRIPTOR_PATTERNS.items():
            for pattern in patterns:
                if pattern in all_text:
                    descriptors.add(category)
                    break
        
        return list(descriptors)
    
    def calculate_sentiment(self, reviews: List[Dict[str, Any]]) -> str:
        """Calculate overall sentiment from review ratings"""
        if not reviews:
            return "neutral"
        
        avg_rating = sum(review.get("rating", 0) for review in reviews) / len(reviews)
        
        if avg_rating >= 4.5:
            return "very positive"
        elif avg_rating >= 4.0:
            return "positive"
        elif avg_rating >= 3.0:
            return "neutral"
        elif avg_rating >= 2.0:
            return "negative"
        else:
            return "very negative"
    
    def create_restaurant_profile(self, restaurant: Dict[str, Any]) -> str:
        """Create a summary profile of the restaurant for LLM matching"""
        name = restaurant.get("name", "")
        cuisine = ", ".join(restaurant.get("cuisine_types", []))
        price = restaurant.get("price_display", "Unknown price range")
        rating = restaurant.get("rating", 0)
        city = restaurant.get('city', '')
        descriptors = restaurant.get("descriptors", [])
        popular_dishes = restaurant.get("popular_dishes", [])
        
        profile = f"{name} is a {cuisine} restaurant in {city} with a {price} price range."
        
        if rating > 0:
            profile += f" It has a rating of {rating}/5."
        
        if descriptors:
            # Convert snake_case to readable format
            readable_descriptors = [desc.replace("_", " ") for desc in descriptors]
            profile += f" It is known for being {', '.join(readable_descriptors[:-1])} and {readable_descriptors[-1]}." if len(readable_descriptors) > 1 else f" It is known for being {readable_descriptors[0]}."
        
        if popular_dishes:
            profile += f" Popular dishes include {', '.join(popular_dishes[:-1])} and {popular_dishes[-1]}." if len(popular_dishes) > 1 else f" A popular dish is {popular_dishes[0]}."
        
        return profile
    
    def generate_cuisine_stats(self) -> Dict[str, int]:
        """Generate statistics about cuisine types"""
        restaurants = self.load_restaurants()
        
        cuisine_counts = {}
        
        for restaurant in restaurants:
            for cuisine in restaurant.get("cuisine_types", []):
                cuisine_counts[cuisine] = cuisine_counts.get(cuisine, 0) + 1
        
        # Sort by count
        return {k: v for k, v in sorted(cuisine_counts.items(), key=lambda item: item[1], reverse=True)}
    
    def generate_price_stats(self) -> Dict[str, int]:
        """Generate statistics about price levels"""
        restaurants = self.load_restaurants()
        
        price_counts = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
        
        for restaurant in restaurants:
            price_level = restaurant.get("price_level", 0)
            price_counts[price_level] += 1
        
        # Convert to labels
        return {PRICE_MAPPING[k]: v for k, v in price_counts.items()}