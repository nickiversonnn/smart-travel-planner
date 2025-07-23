import os
import requests
import math
from typing import Dict, Any
from datetime import datetime, timedelta

def get_safety(city: str) -> Dict[str, Any]:
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        return {
            "error": "News API key not configured",
            "status": "error"
        }
    try:
        url = "https://newsapi.org/v2/everything"
        today = datetime.utcnow().date()
        first_day = today - timedelta(days=1)
        params = {
            "q": f"{city} crime OR theft OR violence",
            "language": "en",
            "pageSize": 100,
            "apiKey": api_key,
            "from": first_day.isoformat(),
            "to": today.isoformat(),
            "page": 1
        }
        resp = requests.get(url, params=params)
        data = resp.json()
        articles = data.get("articles", [])
        total_count = len(articles)
        score = max(0, 100 - 20 * math.log1p(total_count))
        score = round(score)
        return {
            "safety_score": score,
            "articles": total_count,
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