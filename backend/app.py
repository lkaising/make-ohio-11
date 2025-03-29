import os
import argparse
from services.data_collector import GooglePlacesCollector
from utils.data_processor import DataProcessor

def main():
    """Main entry point for the restaurant data collection component"""
    parser = argparse.ArgumentParser(description="Ohio Restaurant Data Collector")
    parser.add_argument('--collect', action='store_true', help='Collect restaurant data')
    parser.add_argument('--cities', nargs='+', help='Specific cities to collect data for (e.g., columbus cleveland)')
    parser.add_argument('--clean', action='store_true', help='Clean the collected data')
    parser.add_argument('--stats', action='store_true', help='Generate statistics about the data')
    
    args = parser.parse_args()
    
    if args.collect:
        print("Starting restaurant data collection...")
        collector = GooglePlacesCollector()
        collector.collect_all_restaurants(args.cities)
        print("Data collection complete!")
    
    if args.clean:
        print("Cleaning restaurant data...")
        processor = DataProcessor()
        processor.clean_data()
        print("Data cleaning complete!")
    
    if args.stats:
        print("Generating statistics...")
        processor = DataProcessor()
        
        cuisine_stats = processor.generate_cuisine_stats()
        print("\nCuisine Types:")
        for cuisine, count in list(cuisine_stats.items())[:15]:  # Show top 15
            print(f"{cuisine}: {count} restaurants")
        
        price_stats = processor.generate_price_stats()
        print("\nPrice Levels:")
        for label, count in price_stats.items():
            print(f"{label}: {count} restaurants")
    
    # If no arguments provided, show help
    if not (args.collect or args.clean or args.stats):
        parser.print_help()

if __name__ == "__main__":
    main()