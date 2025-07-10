import requests
import os
from typing import Dict, Any, Optional

def get_weather(city: str) -> Dict[str, Any]:
    """
    Get current weather data for a city using WeatherAPI.
    
    Args:
        city (str): City name to get weather for
        
    Returns:
        Dict containing weather data or error information
    """
    api_key = os.getenv("WEATHER_API_KEY")
    
    if not api_key:
        return {
            "error": "Weather API key not configured",
            "status": "error"
        }
    
    try:
        url = f"http://api.weatherapi.com/v1/current.json"
        params = {
            "key": api_key,
            "q": city,
            "aqi": "no"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Add weather score calculation
        weather_score = calculate_weather_score(data)
        data["weather_score"] = weather_score
        data["error"] = None
        data["status"] = "success"
        
        return data
        
    except requests.exceptions.RequestException as e:
        return {
            "error": f"Weather API request failed: {str(e)}",
            "status": "error"
        }
    except Exception as e:
        return {
            "error": f"Unexpected error: {str(e)}",
            "status": "error"
        }

def calculate_weather_score(weather_data: Dict[str, Any]) -> int:
    """
    Calculate a weather score based on temperature, conditions, and humidity.
    
    Args:
        weather_data: Weather data from API
        
    Returns:
        Weather score (0-100)
    """
    try:
        current = weather_data.get("current", {})
        temp_f = current.get("temp_f", 0)
        condition_text = current.get("condition", {}).get("text", "").lower()
        humidity = current.get("humidity", 50)
        wind_mph = current.get("wind_mph", 0)
        
        # Temperature scoring (0-40 points)
        if 65 <= temp_f <= 80:
            temp_score = 40  # Perfect temperature
        elif 55 <= temp_f < 65 or 80 < temp_f <= 85:
            temp_score = 30  # Good temperature
        elif 45 <= temp_f < 55 or 85 < temp_f <= 90:
            temp_score = 20  # Acceptable temperature
        else:
            temp_score = 10  # Poor temperature
        
        # Condition scoring (0-40 points)
        if "sunny" in condition_text or "clear" in condition_text:
            condition_score = 40
        elif "partly cloudy" in condition_text or "cloudy" in condition_text:
            condition_score = 35
        elif "overcast" in condition_text:
            condition_score = 25
        elif "rain" in condition_text or "drizzle" in condition_text:
            condition_score = 15
        elif "snow" in condition_text or "sleet" in condition_text:
            condition_score = 10
        elif "storm" in condition_text or "thunder" in condition_text:
            condition_score = 5
        else:
            condition_score = 20  # Default for unknown conditions
        
        # Humidity scoring (0-20 points)
        if 30 <= humidity <= 60:
            humidity_score = 20  # Comfortable humidity
        elif 20 <= humidity < 30 or 60 < humidity <= 70:
            humidity_score = 15  # Acceptable humidity
        else:
            humidity_score = 10  # Poor humidity
        
        total_score = temp_score + condition_score + humidity_score
        return min(100, max(0, total_score))
        
    except Exception:
        return 50  # Default score if calculation fails