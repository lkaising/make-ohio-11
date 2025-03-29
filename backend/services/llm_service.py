import os
import json
import google.generativeai as genai
from typing import List, Dict, Any, Optional
import sys

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATA_DIR

class LLMService:
    """
    Service to process user queries and match them with restaurant recommendations
    using Google's Gemini Pro 2.5 LLM
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the LLM service with the Google Gemini API key
        
        Args:
            api_key: Google Gemini API key (if None, will try to load from environment)
        """
        self.api_key = api_key or os.getenv("GOOGLE_GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Google Gemini API key not provided and not found in environment variables")
        
        # Configure the Google Generative AI library
        genai.configure(api_key=self.api_key)
        
        # Load the restaurant data
        self.restaurants_path = os.path.join(DATA_DIR, "restaurants.json")
        self.restaurants = self._load_restaurants()
    
    def _load_restaurants(self) -> List[Dict[str, Any]]:
        """Load restaurant data from JSON file"""
        if not os.path.exists(self.restaurants_path):
            raise FileNotFoundError(f"Restaurant data not found at {self.restaurants_path}")
        
        with open(self.restaurants_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_recommendations(self, user_query: str, 
                           num_results: int = 3, 
                           city: Optional[str] = None,
                           price_level: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        Get restaurant recommendations based on user query
        
        Args:
            user_query: Natural language query from the user
            num_results: Number of restaurant recommendations to return
            city: Optional city filter
            price_level: Optional price level filter (list of integers 1-4)
            
        Returns:
            Dict containing recommendations and query analysis
        """
        # Filter restaurants by city and price level if provided
        filtered_restaurants = self.restaurants
        
        if city:
            city = city.lower()
            filtered_restaurants = [r for r in filtered_restaurants if r.get("city", "").lower() == city]
        
        if price_level:
            filtered_restaurants = [r for r in filtered_restaurants if r.get("price_level", 0) in price_level]
        
        # Prepare the context for the LLM prompt
        context = self._prepare_context(filtered_restaurants, user_query)
        
        # Generate recommendations using Gemini
        response = self._generate_recommendations(context, user_query, num_results)
        
        return response
    
    def _prepare_context(self, restaurants: List[Dict[str, Any]], 
                        user_query: str) -> str:
        """
        Prepare the context for the LLM prompt
        
        Args:
            restaurants: List of restaurant data
            user_query: Natural language query from the user
            
        Returns:
            String context for the LLM prompt
        """
        # Limit the number of restaurants to avoid token limits (adjust as needed)
        max_restaurants = 100
        if len(restaurants) > max_restaurants:
            # Sort by rating and number of reviews to prioritize popular restaurants
            restaurants = sorted(
                restaurants, 
                key=lambda r: (r.get("rating", 0) * min(r.get("user_ratings_total", 0), 500) / 500), 
                reverse=True
            )[:max_restaurants]
        
        # Create a compact restaurant database for the context
        restaurant_profiles = []
        for idx, restaurant in enumerate(restaurants):
            profile = restaurant.get("profile", "")
            if profile:
                restaurant_profiles.append(f"Restaurant {idx+1}: {profile}")
        
        context = "\n".join(restaurant_profiles)
        
        return context
    
    def _generate_recommendations(self, context: str, 
                                user_query: str, 
                                num_results: int = 3) -> Dict[str, Any]:
        """
        Generate restaurant recommendations using Google Gemini
        
        Args:
            context: Restaurant data context
            user_query: Natural language query from the user
            num_results: Number of restaurant recommendations to return
            
        Returns:
            Dict containing recommendations and query analysis
        """
        # Load the model
        model = genai.GenerativeModel('gemini-2.5-pro-exp-03-25')
        
        # Construct the prompt
        prompt = f"""
You are a restaurant recommendation assistant for Ohio.
Your task is to recommend restaurants based on the user's query.
Use only the restaurant information provided below. Do not make up any restaurants.

USER QUERY: "{user_query}"

RESTAURANT DATABASE:
{context}

Based on the user's query, identify the top {num_results} most relevant restaurants.
For each restaurant, provide:
1. Restaurant name
2. Rating (out of 5)
3. Price level
4. A brief explanation of why it matches the user's query
5. A few key details about the restaurant (cuisine, popular dishes, etc.)

Also provide a brief analysis of what the user seems to be looking for.

Format your response as a JSON object with the following structure:
{{
  "query_analysis": "Brief analysis of what the user is looking for",
  "recommendations": [
    {{
      "name": "Restaurant Name",
      "rating": "4.5/5",
      "price_level": "$",
      "match_reasons": "Why this restaurant matches the query",
      "details": "Key details about this restaurant"
    }},
    ...
  ]
}}

Ensure your response is valid JSON with all values as strings.
"""
        
        # Generate the response
        response = model.generate_content(prompt)
        
        # Parse the JSON from the response
        try:
            json_response = json.loads(response.text)
            return json_response
        except json.JSONDecodeError:
            # If the response isn't proper JSON, try to extract it from the text
            try:
                # Look for JSON between triple backticks
                import re
                json_match = re.search(r'```json\s*(.*?)\s*```', response.text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                    return json.loads(json_str)
                
                # Or try to extract the JSON part directly
                json_match = re.search(r'({[\s\S]*})', response.text)
                if json_match:
                    json_str = json_match.group(1)
                    return json.loads(json_str)
            except (json.JSONDecodeError, AttributeError):
                pass
            
            # If all parsing fails, return a formatted error response
            return {
                "query_analysis": "Unable to analyze query properly",
                "recommendations": [],
                "error": "Failed to parse LLM response"
            }
    
    def get_restaurant_details(self, restaurant_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific restaurant
        
        Args:
            restaurant_id: The place_id of the restaurant
            
        Returns:
            Full restaurant details
        """
        for restaurant in self.restaurants:
            if restaurant.get("place_id") == restaurant_id:
                return restaurant
        
        return {"error": "Restaurant not found"}