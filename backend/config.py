import os
from dotenv import load_dotenv

# Load environment variables from .env file
dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(dotenv_path=dotenv_path)

# API Keys
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

# Ohio geographical boundaries (for broader searches if needed)
OHIO_BOUNDS = {
    "northeast": {"lat": 42.327, "lng": -80.518},
    "southwest": {"lat": 38.403, "lng": -84.820}
}

# Max number of restaurants to fetch per zip code
MAX_RESTAURANTS_PER_ZIP = 20

# Path to the data directory
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")