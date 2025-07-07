# Smart Travel Planner – Full-Stack Travel Recommendation API

A comprehensive travel recommendation system that provides real-time weather data, flight information, safety assessments, and composite travel scores for any destination.

## 🌟 Features

- **Live Weather Data** - Current conditions and temperature via WeatherAPI
- **Flight Information** - Available flights via Aviationstack API  
- **Safety Assessment** - Crime-related news analysis via NewsAPI
- **Composite Scoring** - Intelligent travel recommendations based on multiple factors
- **RESTful API** - Clean, documented endpoints with FastAPI

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- API keys for:
  - [WeatherAPI](https://www.weatherapi.com/) (Free tier available)
  - [Aviationstack](https://aviationstack.com/) (Free tier available)
  - [NewsAPI](https://newsapi.org/) (Free tier available)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd smart-travel-planner
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Run the server**
   ```bash
   python main.py
   ```

The API will be available at `http://127.0.0.1:8000`

## 📚 API Documentation

Once running, visit `http://127.0.0.1:8000/docs` for interactive API documentation.

### Endpoints

#### `GET /`
Health check endpoint
```json
{
  "message": "Smart Travel Planner API is live!"
}
```

#### `GET /weather?city={city}`
Get current weather for a city
```json
{
  "location": {
    "name": "New York",
    "country": "United States of America"
  },
  "current": {
    "temp_f": 72,
    "condition": {
      "text": "Partly cloudy"
    },
    "humidity": 65,
    "wind_mph": 8
  }
}
```

#### `GET /flights?city={city}`
Get available flights to a city
```json
[
  {
    "airline": "American Airlines",
    "flight_number": "AA123",
    "departure_time": "2024-01-15T10:30:00+00:00",
    "arrival_time": "2024-01-15T13:45:00+00:00",
    "departure_airport": "LAX",
    "arrival_airport": "JFK"
  }
]
```

#### `GET /safety?city={city}`
Get safety assessment for a city
```json
{
  "safety_score": 85,
  "articles": 3,
  "risk_level": "Low"
}
```

#### `GET /recommend?city={city}`
Get comprehensive travel recommendation
```json
{
  "destination": "New York",
  "composite_score": 78,
  "recommendation": "Good to visit",
  "weather": {
    "temp_f": 72,
    "condition": "Partly cloudy",
    "score": 85
  },
  "safety": {
    "safety_score": 85,
    "articles": 3,
    "risk_level": "Low"
  },
  "flights": [...],
  "summary": "New York offers pleasant weather and good safety conditions."
}
```

## 🔧 Configuration

Create a `.env` file in the root directory:

```env
WEATHER_API_KEY=your_weather_api_key_here
AVIATIONSTACK_API_KEY=your_aviationstack_api_key_here
NEWS_API_KEY=your_news_api_key_here
```

## 🧠 How It Works

### Weather Scoring
- **Temperature**: Optimal range 65-80°F (100 points)
- **Conditions**: Penalties for rain, snow, extreme weather
- **Humidity**: Comfort factor consideration

### Safety Scoring
- **News Analysis**: Counts recent crime-related articles
- **Scoring**: 100 - (article_count × 10)
- **Risk Levels**: Low (80-100), Medium (60-79), High (0-59)

### Composite Scoring
- **Weather Weight**: 50%
- **Safety Weight**: 50%
- **Final Score**: Weighted average with recommendations

## 🛠️ Development

### Project Structure
```
smart-travel-planner/
├── main.py                  # FastAPI server & endpoints
├── utils/
│   ├── weather_api.py       # Weather API integration
│   ├── flight_api.py        # Flight data processing
│   └── safety_api.py        # Safety assessment logic
├── .env                     # API keys (create from .env.example)
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

### Running Tests
```bash
# Install test dependencies
pip install pytest httpx

# Run tests
pytest
```

### Code Quality
```bash
# Install linting tools
pip install black flake8

# Format code
black .

# Check code style
flake8 .
```

## 🚀 Deployment

### Docker (Optional)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables for Production
- Set all API keys in your deployment environment
- Consider using a secrets management service
- Enable HTTPS in production

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [WeatherAPI](https://www.weatherapi.com/) for weather data
- [Aviationstack](https://aviationstack.com/) for flight information
- [NewsAPI](https://newsapi.org/) for news data
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework

## 📞 Support

For support, email support@smarttravelplanner.com or create an issue in this repository.


