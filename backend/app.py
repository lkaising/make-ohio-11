import os
import argparse
import json
from services.data_collector import GooglePlacesCollector
from utils.data_processor import DataProcessor

def main():
    """Main entry point for the restaurant data collection and processing component"""
    parser = argparse.ArgumentParser(description="Ohio Restaurant Data Collector and Processor")
    parser.add_argument('--collect', action='store_true', help='Collect restaurant data')
    parser.add_argument('--cities', nargs='+', help='Specific cities to collect data for (e.g., columbus cleveland)')
    parser.add_argument('--zipcodes', nargs='+', help='Specific zip codes to collect data for (e.g., 43201 43215)')
    parser.add_argument('--process', action='store_true', help='Process and enhance restaurant data for LLM matching')
    parser.add_argument('--stats', action='store_true', help='Generate statistics about the data')
    parser.add_argument('--view', type=str, help='View a specific restaurant by name or ID')
    parser.add_argument('--all', action='store_true', help='Run full pipeline: collect, process, and show stats')
    
    args = parser.parse_args()
    
    # Handle the --all flag
    if args.all:
        args.collect = True
        args.process = True
        args.stats = True
    
    if args.collect:
        print("\n=== STEP 1: COLLECTING RESTAURANT DATA ===")
        collector = GooglePlacesCollector()
        
        if args.zipcodes:
            print(f"Collecting restaurant data for specific zipcodes: {', '.join(args.zipcodes)}")
            collector.collect_by_zipcodes(args.zipcodes)
        else:
            print(f"Collecting restaurant data for cities: {', '.join(args.cities) if args.cities else 'all'}")
            collector.collect_all_restaurants(args.cities)
            
        print("Data collection complete!")
    
    if args.process:
        print("\n=== STEP 2: PROCESSING RESTAURANT DATA ===")
        processor = DataProcessor()
        print("Cleaning and enhancing restaurant data...")
        processor.clean_data()
        print("Data processing complete!")
    
    if args.stats:
        print("\n=== STEP 3: GENERATING STATISTICS ===")
        processor = DataProcessor()
        
        # Basic stats
        restaurants = processor.load_restaurants()
        print(f"Total restaurants in dataset: {len(restaurants)}")
        
        # Cuisine stats
        cuisine_stats = processor.generate_cuisine_stats()
        print("\nTop Cuisine Types:")
        for cuisine, count in list(cuisine_stats.items())[:10]:  # Show top 10
            print(f"{cuisine}: {count} restaurants")
        
        # Price stats
        price_stats = processor.generate_price_stats()
        print("\nPrice Levels:")
        for label, count in price_stats.items():
            print(f"{label}: {count} restaurants")
        
        # Enhanced data stats
        with_dishes = sum(1 for r in restaurants if r.get("popular_dishes"))
        with_descriptors = sum(1 for r in restaurants if r.get("descriptors"))
        
        print(f"\nEnhanced Data:")
        print(f"Restaurants with extracted dishes: {with_dishes}/{len(restaurants)}")
        print(f"Restaurants with descriptors: {with_descriptors}/{len(restaurants)}")
        
        # Rating distribution
        ratings = {}
        for r in restaurants:
            rating = r.get("rating", 0)
            # Round to nearest 0.5
            rating_key = round(rating * 2) / 2
            ratings[rating_key] = ratings.get(rating_key, 0) + 1
        
        print("\nRating Distribution:")
        for rating in sorted(ratings.keys()):
            print(f"{rating} stars: {ratings[rating]} restaurants")
    
    if args.view:
        processor = DataProcessor()
        restaurants = processor.load_restaurants()
        
        # Case-insensitive partial name matching
        search_term = args.view.lower()
        matches = [r for r in restaurants if search_term in r.get("name", "").lower() or search_term == r.get("place_id", "")]
        
        if matches:
            print(f"\nFound {len(matches)} matching restaurants:")
            for i, restaurant in enumerate(matches):
                print(f"\n--- Restaurant {i+1}: {restaurant.get('name')} ---")
                print(f"Address: {restaurant.get('address')}")
                print(f"Rating: {restaurant.get('rating')}/5 ({restaurant.get('user_ratings_total')} reviews)")
                print(f"Price: {restaurant.get('price_display', restaurant.get('price_level', 'Unknown'))}")
                
                # Show cuisine types if available
                cuisines = restaurant.get("cuisine_types", [])
                if cuisines:
                    print(f"Cuisine: {', '.join(cuisines)}")
                
                # Show popular dishes if available
                dishes = restaurant.get("popular_dishes", [])
                if dishes:
                    print(f"Popular Dishes: {', '.join(dishes)}")
                
                # Show keywords/descriptors if available
                descriptors = restaurant.get("descriptors", [])
                if descriptors:
                    # Convert snake_case to readable format
                    readable = [d.replace("_", " ") for d in descriptors]
                    print(f"Keywords: {', '.join(readable)}")
                
                # Show profile if available
                profile = restaurant.get("profile", "")
                if profile:
                    print(f"Profile: {profile}")
                
                # Show a sample review if available
                reviews = restaurant.get("reviews", [])
                if reviews:
                    top_review = max(reviews, key=lambda r: r.get("rating", 0))
                    if top_review:
                        print(f"\nTop Review ({top_review.get('rating')}/5):")
                        review_text = top_review.get("text", "")
                        # Truncate long reviews
                        if len(review_text) > 200:
                            review_text = review_text[:197] + "..."
                        print(f'"{review_text}"')
        else:
            print(f"No restaurants found matching '{args.view}'")
    
    # If no arguments provided, show help
    if not (args.collect or args.process or args.stats or args.view or args.all):
        parser.print_help()
        print("\nExample usage:")
        print("  python app.py --collect --cities columbus            # Collect data for Columbus")
        print("  python app.py --collect --zipcodes 43201 43215       # Collect data for specific zip codes")
        print("  python app.py --process                             # Process collected data")
        print("  python app.py --all                                 # Run complete pipeline")
        print("  python app.py --view burger                         # View restaurants with 'burger' in name")

if __name__ == "__main__":
    main()