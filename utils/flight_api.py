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
        
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        
        # Check for API errors
        if "error" in data:
            return {
                "error": f"Aviationstack API error: {data['error'].get('message', 'Unknown error')}",
                "status": "error"
            }
        
        flights_data = data.get("data", [])
        
        # Process and simplify flight data
        simplified_flights = process_flights(flights_data)
        
        # Calculate flight availability score
        availability_score = calculate_availability_score(simplified_flights)
        
        return {
            "flights": simplified_flights,
            "total_flights": len(simplified_flights),
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

def process_flights(flights_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Process and simplify flight data from Aviationstack API.
    
    Args:
        flights_data: Raw flight data from API
        
    Returns:
        List of simplified flight information
    """
    simplified = []
    
    for flight in flights_data:
        try:
            # Extract airline information
            airline = flight.get("airline", {})
            airline_name = airline.get("name", "Unknown Airline")
            airline_iata = airline.get("iata", "")
            
            # Extract flight information
            flight_info = flight.get("flight", {})
            flight_number = flight_info.get("iata", "")
            flight_number_full = flight_info.get("number", "")
            
            # Extract departure information
            departure = flight.get("departure", {})
            departure_airport = departure.get("airport", "Unknown")
            departure_iata = departure.get("iata", "")
            departure_time = departure.get("scheduled", "")
            departure_delay = departure.get("delay", 0)
            
            # Extract arrival information
            arrival = flight.get("arrival", {})
            arrival_airport = arrival.get("airport", "Unknown")
            arrival_iata = arrival.get("iata", "")
            arrival_time = arrival.get("scheduled", "")
            arrival_delay = arrival.get("delay", 0)
            
            # Extract aircraft information
            aircraft = flight.get("aircraft", {})
            aircraft_type = aircraft.get("icao24", "")
            
            # Extract flight status
            flight_status = flight.get("flight_status", "unknown")
            
            # Format times if available
            departure_time_formatted = format_time(departure_time)
            arrival_time_formatted = format_time(arrival_time)
            
            simplified_flight = {
                "airline": {
                    "name": airline_name,
                    "iata": airline_iata
                },
                "flight": {
                    "number": flight_number,
                    "number_full": flight_number_full
                },
                "departure": {
                    "airport": departure_airport,
                    "iata": departure_iata,
                    "scheduled": departure_time_formatted,
                    "delay": departure_delay
                },
                "arrival": {
                    "airport": arrival_airport,
                    "iata": arrival_iata,
                    "scheduled": arrival_time_formatted,
                    "delay": arrival_delay
                },
                "aircraft": aircraft_type,
                "status": flight_status
            }
            
            simplified.append(simplified_flight)
            
        except Exception as e:
            # Skip flights with processing errors
            continue
    
    return simplified

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
        airline_name = flight.get("airline", {}).get("name", "")
        if airline_name:
            airlines.add(airline_name)
    
    variety_score = min(30, len(airlines) * 5)
    
    # Status score (active flights)
    active_flights = sum(1 for flight in flights 
                        if flight.get("status", "").lower() in ["active", "scheduled"])
    status_score = min(30, (active_flights / len(flights)) * 30) if flights else 0
    
    total_score = count_score + variety_score + status_score
    return min(100, int(total_score))