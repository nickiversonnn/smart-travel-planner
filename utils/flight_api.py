import os
import requests

def get_flights(city):
    access_key = os.getenv("AVIATIONSTACK_API_KEY")
    url = "http://api.aviationstack.com/v1/flights"
    params = {
        "access_key": access_key,
        "limit": 5,
        "arr_city": city
    }

    resp = requests.get(url, params=params)
    data = resp.json().get("data", [])
    
    simplified = []
    for flight in data:
        simplified.append({
            "airline": flight.get("airline", {}).get("name"),
            "flight_number": flight.get("flight", {}).get("iata"),
            "departure_time": flight.get("departure", {}).get("scheduled"),
            "arrival_time": flight.get("arrival", {}).get("scheduled"),
            "departure_airport": flight.get("departure", {}).get("airport"),
            "arrival_airport": flight.get("arrival", {}).get("airport")
        })

    return simplified