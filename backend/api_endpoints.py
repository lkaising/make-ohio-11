from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn

from services.llm_service import LLMService

# Initialize the FastAPI app
app = FastAPI(title="Ohio Restaurant Finder API")

# Add CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the LLM service
llm_service = LLMService()

# Request and response models
class RecommendationRequest(BaseModel):
    query: str
    num_results: int = 3
    city: Optional[str] = None
    price_levels: Optional[List[int]] = None

class RecommendationResponse(BaseModel):
    query_analysis: str
    recommendations: List[Dict[str, Any]]
    error: Optional[str] = None

@app.get("/")
def read_root():
    return {"status": "Restaurant Finder API is running"}

@app.post("/recommendations", response_model=RecommendationResponse)
def get_recommendations(request: RecommendationRequest):
    """
    Get restaurant recommendations based on user query
    """
    try:
        results = llm_service.get_recommendations(
            user_query=request.query,
            num_results=request.num_results,
            city=request.city,
            price_level=request.price_levels
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/restaurant/{restaurant_id}")
def get_restaurant_details(restaurant_id: str):
    """
    Get detailed information about a specific restaurant
    """
    result = llm_service.get_restaurant_details(restaurant_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@app.get("/cities")
def get_cities():
    """
    Get list of available cities
    """
    cities = set()
    for restaurant in llm_service.restaurants:
        city = restaurant.get("city")
        if city:
            cities.add(city)
    return {"cities": sorted(list(cities))}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)