# 🌦️ French Weather Analytics

A simple Streamlit app to visualize weather data for French cities.

## Features

- **Real-time Weather**: Current weather for major French cities
- **City Comparison**: Compare weather between different cities
- **5-Day Forecast**: Simple weather forecast visualization
- **Clean Interface**: Easy to use dashboard

## Project Structure

```
french-weather-app/
├── src/
│   ├── app.py                 # Main Streamlit app
│   ├── weather_api.py         # Weather API calls
│   ├── data_processor.py      # Data processing
│   ├── models.py             # Simple prediction models
│   └── config.py             # App configuration
├── tests/
│   └── unit/                 # Unit tests
├── requirements.txt          # Dependencies
├── Dockerfile               # Docker setup
└── docker-compose.yml       # Docker compose
```

## Setup

1. **Get API Key**
   - Sign up at https://openweathermap.org/api
   - Get your free API key

2. **Install**
```bash
pip install -r requirements.txt
```

3. **Set API Key**
Create a `.env` file:
```
OPENWEATHER_API_KEY=your_api_key_here
```

4. **Run**
```bash
streamlit run src/app.py
```

### Using Docker
```bash
docker-compose up --build
```

## Testing

Run tests:
```bash
pytest tests/
```

## What I learned

This project helped me learn:
- How to use APIs in Python
- Building web apps with Streamlit
- Data visualization with Plotly
- Basic testing with pytest
- Docker containerization
