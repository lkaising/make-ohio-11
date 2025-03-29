import os
import json
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).resolve().parent / "backend"
sys.path.append(str(backend_dir))

# Import the LLMService class
from services.llm_service import LLMService

def test_llm():
    """
    Test the LLM service with a few example queries
    """
    # Create an instance of the LLMService
    try:
        llm_service = LLMService()
        print("LLM service initialized successfully")
    except Exception as e:
        print(f"Failed to initialize LLM service: {e}")
        return

    # Define some test queries
    test_queries = [
        "I'm looking for a place similar to McDonald's but not McDonald's, with cheap and yummy burgers",
        "I want a romantic Italian restaurant for a date night",
        "Where can I find authentic Mexican food in Columbus?"
    ]

    # Test each query
    for i, query in enumerate(test_queries):
        print(f"\n\n--- Testing Query {i+1}: '{query}' ---\n")
        
        try:
            # Get recommendations
            results = llm_service.get_recommendations(
                user_query=query,
                num_results=3,
                city=None,
                price_level=None
            )
            
            # Print the query analysis
            print(f"Query Analysis: {results['query_analysis']}\n")
            
            # Print the recommendations
            print("Recommendations:")
            for j, restaurant in enumerate(results['recommendations']):
                print(f"\n{j+1}. {restaurant['name']} - {restaurant['rating']} - {restaurant['price_level']}")
                print(f"   Match Reason: {restaurant['match_reasons']}")
                print(f"   Details: {restaurant['details']}")
            
            # Print if there was an error
            if 'error' in results:
                print(f"\nError: {results['error']}")
                
        except Exception as e:
            print(f"Error processing query: {e}")

    print("\n\n--- Testing Complete ---")

if __name__ == "__main__":
    test_llm()