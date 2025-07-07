#!/usr/bin/env python3
"""
Simple test script for the Smart Travel Planner API.
Run this after starting the server to test the endpoints.
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    """Test the health check endpoint"""
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_weather(city="New York"):
    """Test the weather endpoint"""
    print(f"Testing weather for {city}...")
    response = requests.get(f"{BASE_URL}/weather", params={"city": city})
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Temperature: {data.get('current', {}).get('temp_f')}°F")
        print(f"Weather Score: {data.get('weather_score')}")
    else:
        print(f"Error: {response.text}")
    print()

def test_safety(city="New York"):
    """Test the safety endpoint"""
    print(f"Testing safety for {city}...")
    response = requests.get(f"{BASE_URL}/safety", params={"city": city})
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Safety Score: {data.get('safety_score')}")
        print(f"Risk Level: {data.get('risk_level')}")
        print(f"Articles Count: {data.get('articles_count')}")
    else:
        print(f"Error: {response.text}")
    print()

def test_flights(city="New York"):
    """Test the flights endpoint"""
    print(f"Testing flights to {city}...")
    response = requests.get(f"{BASE_URL}/flights", params={"city": city})
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total Flights: {data.get('total_flights')}")
        print(f"Availability Score: {data.get('availability_score')}")
        flights = data.get('flights', [])
        if flights:
            print(f"Sample Flight: {flights[0].get('airline', {}).get('name')} {flights[0].get('flight', {}).get('number')}")
    else:
        print(f"Error: {response.text}")
    print()

def test_recommendation(city="New York"):
    """Test the recommendation endpoint"""
    print(f"Testing recommendation for {city}...")
    response = requests.get(f"{BASE_URL}/recommend", params={"city": city})
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Destination: {data.get('destination')}")
        print(f"Composite Score: {data.get('composite_score')}")
        print(f"Recommendation: {data.get('recommendation')}")
        print(f"Summary: {data.get('summary')}")
    else:
        print(f"Error: {response.text}")
    print()

def main():
    """Run all tests"""
    print("🚀 Smart Travel Planner API Tests")
    print("=" * 50)
    
    try:
        test_health()
        test_weather("New York")
        test_safety("New York")
        test_flights("New York")
        test_recommendation("New York")
        
        print("✅ All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API server.")
        print("Make sure the server is running with: python main.py")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    main() 