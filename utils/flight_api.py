import os
import requests
from typing import Dict, Any
from datetime import datetime, timedelta
import csv


def city_to_iata(city: str, csv_path: str = "airports.csv") -> str:
    city = city.strip().lower()
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['city'].strip().lower() == city and row['iata']:
                return row['iata']
    return None


def get_flights(city: str) -> Dict[str, Any]:
    api_key = os.getenv("AERODATABOX_API_KEY")
    if not api_key:
        print("[ERROR] AeroDataBox API key not configured")
        return {
            "error": "AeroDataBox API key not configured",
            "status": "error"
        }
    try:
        iata = city_to_iata(city)
        if not iata:
            return {
                "error": f"Could not find IATA code for city '{city}'",
                "status": "error"
            }
        # Use a 12-hour window from now
        now = datetime.utcnow()
        from_time = now.strftime('%Y-%m-%dT%H:00')
        to_time = (now + timedelta(hours=12)).strftime('%Y-%m-%dT%H:00')
        url = f"https://aerodatabox.p.rapidapi.com/flights/airports/iata/{iata}/{from_time}/{to_time}"
        headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "aerodatabox.p.rapidapi.com"
        }
        params = {
            "withLeg": "true",
            "direction": "Both",
            "withCancelled": "true",
            "withCodeshared": "true",
            "withCargo": "true",
            "withPrivate": "true",
            "withLocation": "false"
        }
        print(f"[INFO] Requesting: {url}")
        resp = requests.get(url, headers=headers, params=params)
        print(f"[INFO] Status: {resp.status_code}")
        print(f"[DEBUG] Response: {resp.text}")
        data = resp.json()
        flights = []
        for f in data.get("departures", []) + data.get("arrivals", []):
            airline = f.get("airline", {}).get("name")
            flight_number = f.get("number") or f.get("flightNumber")
            dep_airport = f.get("departure", {}).get("airport", {}).get("name")
            arr_airport = f.get("arrival", {}).get("airport", {}).get("name")
            dep_time = f.get("departure", {}).get("scheduledTime", {}).get("local")
            arr_time = f.get("arrival", {}).get("scheduledTime", {}).get("local")
            flights.append({
                    "airline": airline,
                    "flight_number": flight_number,
                    "departure_airport": dep_airport,
                    "arrival_airport": arr_airport,
                    "departure_time": dep_time,
                    "arrival_time": arr_time
            })
        useful_flights = flights
        unique_airlines = set(f["airline"] for f in useful_flights if f.get("airline"))
        flight_score = min(len(useful_flights), 150) / 150 * 60
        airline_score = min(len(unique_airlines), 8) / 8 * 40
        availability_score = int(flight_score + airline_score)
        return {
            "flights": useful_flights[:10],
            "total_flights": len(useful_flights),
            "unique_airlines": len(unique_airlines),
            "availability_score": availability_score,
            "status": "success"
        }
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] AeroDataBox API request failed: {e}")
        return {
            "error": f"AeroDataBox API request failed: {str(e)}",
            "status": "error"
        }
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return {
            "error": f"Unexpected error: {str(e)}",
            "status": "error"
        }