from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
from utils.weather_api import get_weather
from utils.flight_api import get_flights
from utils.safety_api import get_safety
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="Smart Travel Planner API",
    description="A comprehensive travel recommendation system providing weather, safety, and flight data",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Response models
class WeatherResponse(BaseModel):
    location: Optional[Dict[str, Any]]
    current: Optional[Dict[str, Any]]
    weather_score: Optional[int]
    error: Optional[str] = None
    status: str

class SafetyResponse(BaseModel):
    safety_score: int
    articles: int
    status: str

class FlightResponse(BaseModel):
    flights: Optional[list]
    total_flights: Optional[int]
    availability_score: Optional[int]
    error: Optional[str] = None
    status: str

class RecommendationResponse(BaseModel):
    destination: str
    composite_score: int
    recommendation: str
    weather: Dict[str, Any]
    safety: Dict[str, Any]
    flights: Dict[str, Any]
    summary: str
    status: str

@app.get("/", tags=["Health"])
def root():
    """Health check endpoint"""
    return {
        "message": "Smart Travel Planner API is live!",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/weather", response_model=WeatherResponse, tags=["Weather"])
def weather(city: str = Query(..., description="City name to fetch weather for", min_length=1)):
    """
    Get current weather data for a city.
    
    - **city**: Name of the city to get weather for
    """
    if not city.strip():
        raise HTTPException(status_code=400, detail="City name cannot be empty")
    
    data = get_weather(city.strip())
    
    if data.get("status") == "error":
        raise HTTPException(status_code=500, detail=data.get("error", "Weather data unavailable"))
    
    return data

@app.get("/flights", response_model=FlightResponse, tags=["Flights"])
def flights(city: str = Query(..., description="City name to get flights for", min_length=1)):
    """
    Get available flights to an airport by city name.
    - **city**: Name of the city to assess flights for
    """
    if not city.strip():
        raise HTTPException(status_code=400, detail="City name cannot be empty")
    data = get_flights(city.strip().upper())
    if data.get("status") == "error":
        raise HTTPException(status_code=500, detail=data.get("error", "Flight data unavailable"))
    return data

@app.get("/safety", response_model=SafetyResponse, tags=["Safety"])
def safety(city: str = Query(..., description="City name to assess safety for", min_length=1)):
    """
    Get safety assessment for a city.
    
    - **city**: Name of the city to assess safety for
    """
    if not city.strip():
        raise HTTPException(status_code=400, detail="City name cannot be empty")
    
    data = get_safety(city.strip())
    
    if data.get("status") == "error":
        raise HTTPException(status_code=500, detail=data.get("error", "Safety data unavailable"))
    
    return data

@app.get("/recommend", response_model=RecommendationResponse, tags=["Recommendations"])
def recommend(city: str = Query(..., description="City name for travel recommendation", min_length=1)):
    """
    Get comprehensive travel recommendation for a city.
    
    This endpoint combines weather, safety, and flight data to provide
    a complete travel assessment with a composite score.
    
    - **city**: Name of the city for travel recommendation
    """
    if not city.strip():
        raise HTTPException(status_code=400, detail="City name cannot be empty")
    
    city = city.strip()
    
    # Get all data
    weather_data = get_weather(city)
    safety_data = get_safety(city)
    flight_data = get_flights(city)
    
    # Check for errors in any of the services
    errors = []
    if weather_data.get("status") == "error":
        errors.append(f"Weather: {weather_data.get('error', 'Unknown error')}")
    if safety_data.get("status") == "error":
        errors.append(f"Safety: {safety_data.get('error', 'Unknown error')}")
    if flight_data.get("status") == "error":
        errors.append(f"Flights: {flight_data.get('error', 'Unknown error')}")
    
    if errors:
        raise HTTPException(
            status_code=500, 
            detail=f"Some services are unavailable: {'; '.join(errors)}"
        )
    
    # Calculate composite score
    composite_score, recommendation, summary = calculate_composite_score(
        weather_data, safety_data, flight_data, city
    )
    
    return {
        "destination": city,
        "composite_score": composite_score,
        "recommendation": recommendation,
        "weather": {
            "temp_f": weather_data.get("current", {}).get("temp_f"),
            "condition": weather_data.get("current", {}).get("condition", {}).get("text"),
            "score": weather_data.get("weather_score", 0),
            "humidity": weather_data.get("current", {}).get("humidity"),
            "wind_mph": weather_data.get("current", {}).get("wind_mph")
        },
        "safety": {
            "safety_score": safety_data.get("safety_score", 0),
            "risk_level": safety_data.get("risk_level", "Unknown"),
            "articles_count": safety_data.get("articles_count", 0),
            "recent_articles": safety_data.get("recent_articles", [])
        },
        "flights": {
            "total_flights": flight_data.get("total_flights", 0),
            "availability_score": flight_data.get("availability_score", 0),
            "sample_flights": flight_data.get("flights", [])[:3]  # Top 3 flights
        },
        "summary": summary,
        "status": "success"
    }

def calculate_composite_score(weather_data: Dict[str, Any], 
                            safety_data: Dict[str, Any], 
                            flight_data: Dict[str, Any],
                            city: str) -> tuple[int, str, str]:
    """
    Calculate composite travel score and generate recommendation.
    
    Args:
        weather_data: Weather information
        safety_data: Safety assessment
        flight_data: Flight availability
        city: City name for summary generation
        
    Returns:
        Tuple of (composite_score, recommendation, summary)
    """
    # Extract scores
    weather_score = weather_data.get("weather_score", 50)
    safety_score = safety_data.get("safety_score", 50)
    flight_score = flight_data.get("availability_score", 50)
    
    # Weighted scoring (weather and safety are more important than flights)
    weather_weight = 0.4
    safety_weight = 0.4
    flight_weight = 0.2
    
    composite_score = int(
        (weather_score * weather_weight) + 
        (safety_score * safety_weight) + 
        (flight_score * flight_weight)
    )
    
    # Generate recommendation
    if composite_score >= 80:
        recommendation = "Excellent destination"
    elif composite_score >= 70:
        recommendation = "Good to visit"
    elif composite_score >= 60:
        recommendation = "Consider visiting"
    elif composite_score >= 50:
        recommendation = "Proceed with caution"
    else:
        recommendation = "Not recommended"
    
    # Generate summary
    weather_condition = weather_data.get("current", {}).get("condition", {}).get("text", "Unknown")
    temp_f = weather_data.get("current", {}).get("temp_f", 0)
    risk_level = safety_data.get("risk_level", "Unknown")
    flight_count = flight_data.get("total_flights", 0)
    
    summary_parts = []
    
    # Weather summary
    if weather_score >= 80:
        summary_parts.append(f"Excellent weather conditions with {weather_condition.lower()} and {temp_f}°F")
    elif weather_score >= 60:
        summary_parts.append(f"Good weather with {weather_condition.lower()} and {temp_f}°F")
    else:
        summary_parts.append(f"Challenging weather with {weather_condition.lower()} and {temp_f}°F")
    
    # Safety summary
    if safety_score >= 80:
        summary_parts.append(f"very safe conditions")
    elif safety_score >= 60:
        summary_parts.append(f"moderate safety with {risk_level.lower()} risk")
    else:
        summary_parts.append(f"concerning safety with {risk_level.lower()} risk")
    
    # Flight summary
    if flight_count > 0:
        summary_parts.append(f"with {flight_count} available flights")
    else:
        summary_parts.append("with limited flight options")
    
    summary = f"{city} offers {', '.join(summary_parts)}."
    
    return composite_score, recommendation, summary

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)