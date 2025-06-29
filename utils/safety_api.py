import os, requests

def get_safety(city):
    api_key = os.getenv("NEWS_API_KEY")
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": f"{city} crime OR theft OR violence",
        "language": "en",
        "pageSize": 10,
        "apiKey": api_key
    }
    resp = requests.get(url, params=params)
    count = len(resp.json().get("articles", []))
    score = max(0, 100 - count*10)
    return {"safety_score": score, "articles": count}