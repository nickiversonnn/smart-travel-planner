import os
import requests
from typing import Dict, Any, List

def get_safety(city: str) -> Dict[str, Any]:
    """
    Get safety assessment for a city using NewsAPI.
    
    Args:
        city (str): City name to assess safety for
        
    Returns:
        Dict containing safety score and risk assessment
    """
    api_key = os.getenv("NEWS_API_KEY")
    
    if not api_key:
        return {
            "error": "News API key not configured",
            "status": "error"
        }
    
    try:
        # Search for crime-related news in the city
        crime_keywords = [
            f"{city} crime",
            f"{city} theft", 
            f"{city} violence",
            f"{city} assault",
            f"{city} robbery",
            f"{city} shooting"
        ]
        
        total_articles = 0
        recent_articles = []
        
        for keyword in crime_keywords:
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": keyword,
                "language": "en",
                "pageSize": 5,
                "sortBy": "publishedAt",
                "apiKey": api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            articles = data.get("articles", [])
            total_articles += len(articles)
            
            # Collect recent articles for analysis
            for article in articles:
                if article.get("title") and article.get("description"):
                    recent_articles.append({
                        "title": article.get("title"),
                        "description": article.get("description"),
                        "publishedAt": article.get("publishedAt")
                    })
        
        # Calculate safety score
        safety_score = calculate_safety_score(total_articles, recent_articles)
        risk_level = get_risk_level(safety_score)
        
        return {
            "safety_score": safety_score,
            "risk_level": risk_level,
            "articles_count": total_articles,
            "recent_articles": recent_articles[:3],  # Top 3 most recent
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

def calculate_safety_score(article_count: int, articles: List[Dict[str, Any]]) -> int:
    """
    Calculate safety score based on crime-related news articles.
    
    Args:
        article_count: Number of crime-related articles found
        articles: List of article details for analysis
        
    Returns:
        Safety score (0-100)
    """
    # Base score starts at 100
    base_score = 100
    
    # Deduct points for each article (diminishing returns)
    if article_count == 0:
        return 100
    elif article_count == 1:
        deduction = 5
    elif article_count == 2:
        deduction = 12
    elif article_count == 3:
        deduction = 18
    elif article_count == 4:
        deduction = 25
    elif article_count == 5:
        deduction = 32
    else:
        # For 6+ articles, cap the deduction
        deduction = min(40, 32 + (article_count - 5) * 2)
    
    # Analyze article severity
    severity_bonus = analyze_article_severity(articles)
    
    final_score = max(0, base_score - deduction + severity_bonus)
    return int(final_score)

def analyze_article_severity(articles: List[Dict[str, Any]]) -> int:
    """
    Analyze the severity of crime-related articles.
    
    Args:
        articles: List of article details
        
    Returns:
        Severity adjustment (-10 to +10)
    """
    severity_keywords = {
        "high": ["shooting", "murder", "homicide", "terrorism", "bomb"],
        "medium": ["assault", "robbery", "theft", "burglary"],
        "low": ["vandalism", "dispute", "argument"]
    }
    
    total_adjustment = 0
    
    for article in articles:
        title = article.get("title", "").lower()
        description = article.get("description", "").lower()
        text = f"{title} {description}"
        
        # Check for high severity keywords
        if any(keyword in text for keyword in severity_keywords["high"]):
            total_adjustment -= 3
        # Check for medium severity keywords
        elif any(keyword in text for keyword in severity_keywords["medium"]):
            total_adjustment -= 1
        # Check for low severity keywords
        elif any(keyword in text for keyword in severity_keywords["low"]):
            total_adjustment += 1
    
    return max(-10, min(10, total_adjustment))

def get_risk_level(safety_score: int) -> str:
    """
    Determine risk level based on safety score.
    
    Args:
        safety_score: Safety score (0-100)
        
    Returns:
        Risk level string
    """
    if safety_score >= 80:
        return "Low"
    elif safety_score >= 60:
        return "Medium"
    elif safety_score >= 40:
        return "High"
    else:
        return "Very High"