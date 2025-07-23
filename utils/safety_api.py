import os
import requests
from typing import Dict, Any

def get_safety(city: str) -> Dict[str, Any]:
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        return {
            "error": "News API key not configured",
            "status": "error"
        }
    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": f"{city} crime OR theft OR violence",
            "language": "en",
            "pageSize": 100,
            "apiKey": api_key
        }
        resp = requests.get(url, params=params)
        count = len(resp.json().get("articles", []))
        score = max(0, 100 - count)
        return {
            "safety_score": score,
            "articles": count,
            "status": "success"
        }
    except requests.exceptions.RequestException as e:
        return {
            "error": f"News API request failed: {str(e)}",
            "status": "error"
        }
    except Exception as e:
        return {
            "error": f"Unexpected error: {str(e)}",
            "status": "error"
        }