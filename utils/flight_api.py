import os
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime

def get_flights(city: str) -> Dict[str, Any]:
    """
    Get flight information for a city using Aviationstack API.
    
    Args:
        city (str): City name to get flights for
        
    Returns:
        Dict containing flight data or error information
    """
    access_key = os.getenv("AVIATIONSTACK_API_KEY")
    
    if not access_key:
        return {
            "error": "Aviationstack API key not configured",
            "status": "error"
        }
    
    try:
        url = "http://api.aviationstack.com/v1/flights"
        params = {
            "access_key": access_key,
            "limit": 10,
            "arr_city": city
        }

        resp = requests.get(url, params=params)
        data = resp.json().get("data", [])
        
        # Process and enhance flight data
        enhanced_flights = []
        for flight in data:
            # Safely extract nested data with null checks
            airline = flight.get("airline", {}) or {}
            flight_info = flight.get("flight", {}) or {}
            departure = flight.get("departure", {}) or {}
            arrival = flight.get("arrival", {}) or {}
            aircraft = flight.get("aircraft", {}) or {}
            
            enhanced_flight = {
                "airline": {
                    "name": airline.get("name", "Unknown Airline"),
                    "iata": airline.get("iata", "")
                },
                "flight": {
                    "number": flight_info.get("iata", ""),
                    "number_full": flight_info.get("number", "")
                },
                "departure": {
                    "airport": departure.get("airport", "Unknown"),
                    "iata": departure.get("iata", ""),
                    "scheduled": format_time(departure.get("scheduled", "")),
                    "delay": departure.get("delay", 0)
                },
                "arrival": {
                    "airport": arrival.get("airport", "Unknown"),
                    "iata": arrival.get("iata", ""),
                    "scheduled": format_time(arrival.get("scheduled", "")),
                    "delay": arrival.get("delay", 0)
                },
                "aircraft": aircraft.get("icao24", ""),
                "status": flight.get("flight_status", "unknown")
            }
            enhanced_flights.append(enhanced_flight)

        # Calculate availability score
        availability_score = calculate_availability_score(enhanced_flights)

        return {
            "flights": enhanced_flights,
            "total_flights": len(enhanced_flights),
            "availability_score": availability_score,
            "status": "success"
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "error": f"Aviationstack API request failed: {str(e)}",
            "status": "error"
        }
    except Exception as e:
        return {
            "error": f"Unexpected error: {str(e)}",
            "status": "error"
        }

def format_time(time_str: str) -> str:
    """
    Format time string for better readability.
    
    Args:
        time_str: Time string from API
        
    Returns:
        Formatted time string
    """
    if not time_str:
        return "Unknown"
    
    try:
        # Try to parse and format the time
        dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return time_str

def calculate_availability_score(flights: List[Dict[str, Any]]) -> int:
    """
    Calculate flight availability score based on number and variety of flights.
    
    Args:
        flights: List of flight information
        
    Returns:
        Availability score (0-100)
    """
    if not flights:
        return 0
    
    # Base score from number of flights
    flight_count = len(flights)
    if flight_count >= 10:
        count_score = 40
    elif flight_count >= 5:
        count_score = 30
    elif flight_count >= 3:
        count_score = 20
    else:
        count_score = 10
    
    # Variety score (different airlines)
    airlines = set()
    for flight in flights:
        airline = flight.get("airline", {}) or {}
        airline_name = airline.get("name", "")
        if airline_name and airline_name != "Unknown Airline":
            airlines.add(airline_name)
    
    variety_score = min(30, len(airlines) * 5)
    
    # Status score (active flights)
    active_flights = sum(1 for flight in flights 
                        if flight.get("status", "").lower() in ["active", "scheduled"])
    status_score = min(30, (active_flights / len(flights)) * 30) if flights else 0
    
    total_score = count_score + variety_score + status_score
    return min(100, int(total_score))