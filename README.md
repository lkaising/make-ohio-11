# Restaurant Finder App - Hackathon Project

A restaurant recommendation app that matches user prompts like "I want something similar to McDonald's but not McDonald's" to relevant restaurants in Ohio.

## Project Structure

```
.
├── backend/
│   ├── app.py                 # Main application
│   ├── config.py              # Configuration and API keys
│   ├── data/
│   │   ├── ohio_zipcodes.json # List of Ohio zip codes
│   │   └── restaurants.json   # Collected restaurant data
│   ├── requirements.txt       # Python dependencies
│   ├── services/
│   │   ├── data_collector.py  # Restaurant data collection
│   │   └── llm_service.py     # LLM integration for recommendations
│   └── utils/
│       └── data_processor.py  # Data cleaning utilities
│
└── frontend/
    ├── public/                # Static files
    ├── src/                   # React source code
    │   ├── components/        # UI components
    │   │   ├── Header.js
    │   │   ├── ResultCard.js
    │   │   └── SearchBar.js
    │   ├── App.js             # Main React app
    │   └── index.js           # Entry point
    └── package.json           # Frontend dependencies
```

## Setup Instructions

### Backend Setup

1. Set up API keys:
   Create a `.env` file in the `backend` directory with the following content:
   ```
   GOOGLE_PLACES_API_KEY=your_google_places_api_key
   OPENAI_API_KEY=your_openai_api_key
   # Or if using Claude
   ANTHROPIC_API_KEY=your_anthropic_api_key
   ```

2. Install dependencies:
   ```
   cd backend
   pip install -r requirements.txt
   ```

3. Collect restaurant data:
   ```
   python app.py --collect
   ```
   
   To collect data for specific cities only:
   ```
   python app.py --collect --cities columbus cleveland
   ```

4. Clean the collected data:
   ```
   python app.py --clean
   ```

5. Generate statistics about the data:
   ```
   python app.py --stats
   ```

### Frontend Setup

1. Install dependencies:
   ```
   cd frontend
   npm install
   ```

2. Start the development server:
   ```
   npm start
   ```

## Features

- Data collection from Google Places API
- Natural language restaurant recommendations
- Simple and intuitive user interface
- Ohio-specific restaurant database

## Technologies Used

- **Backend**: Python, FastAPI, LangChain, Google Places API
- **Frontend**: React, Tailwind CSS
- **LLM**: OpenAI API or Anthropic Claude API