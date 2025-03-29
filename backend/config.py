import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
GOOGLE_PLACES_API_KEY = os.getenv("AIzaSyA1iBohbnQY7GSmcJDJOjFP9SjNzbt1ukI")
# Or if using Outscraper
# OUTSCRAPER_API_KEY = os.getenv("OUTSCRAPER_API_KEY")

# LLM API Keys (for the second component)
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Ohio geographical boundaries (for broader searches if needed)
OHIO_BOUNDS = {
    "northeast": {"lat": 42.327, "lng": -80.518},
    "southwest": {"lat": 38.403, "lng": -84.820}
}

# Max number of restaurants to fetch per zip code
MAX_RESTAURANTS_PER_ZIP = 20

# Path to the data directory
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")