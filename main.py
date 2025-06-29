from fastapi import FastAPI, Query
from utils.weather_api import get_weather
from utils.flight_api import get_flights
from utils.safety_api import get_safety
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Smart Travel Planner API is live!"}

@app.get("/recommend")
def recommend(city: str):
    weather_data = get_weather(city)
    safety_data = get_safety(city)
    flight_data = get_flights(city)

    # Compute weather score (simplified)
    temp = weather_data.get("current", {}).get("temp_f", 0)
    condition = weather_data.get("current", {}).get("condition", {}).get("text", "").lower()
    weather_score = 100 if 65 <= temp <= 80 and "rain" not in condition else 60

    # Safety score comes directly
    safety_score = safety_data.get("safety_score", 50)

    # Composite score (weighted)
    final_score = int((weather_score * 0.5) + (safety_score * 0.5))

    return {
        "destination": city,
        "composite_score": final_score,
        "weather": {
            "temp_f": temp,
            "condition": condition,
            "score": weather_score
        },
        "safety": safety_data,
        "flights": flight_data
    }

@app.get("/weather")
def weather(city: str = Query(..., description="City name to fetch weather for")):
    data = get_weather(city)
    return data

@app.get("/flights")
def flights(city: str):
    return get_flights(city)

@app.get("/safety")
def safety(city: str):
    return get_safety(city)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)