"""OpenWeatherMap API integration for French weather data."""

import requests
import streamlit as st
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta
import json

try:
    from .config import (
        OPENWEATHER_API_KEY, 
        OPENWEATHER_BASE_URL, 
        CACHE_TTL,
        TEMPERATURE_UNIT,
        LANGUAGE
    )
except ImportError:
    from config import (
        OPENWEATHER_API_KEY, 
        OPENWEATHER_BASE_URL, 
        CACHE_TTL,
        TEMPERATURE_UNIT,
        LANGUAGE
    )


class WeatherAPIError(Exception):
    """Custom exception for weather API errors."""
    pass


class WeatherAPI:
    """Handle all interactions with OpenWeatherMap API."""
    
    def __init__(self):
        if not OPENWEATHER_API_KEY:
            raise WeatherAPIError("OpenWeatherMap API key not found. Please set OPENWEATHER_API_KEY environment variable.")
        
        self.api_key = OPENWEATHER_API_KEY
        self.base_url = OPENWEATHER_BASE_URL
        self.session = requests.Session()
        
    def _make_request(self, endpoint: str, params: Dict) -> Dict:
        """Make a request to the OpenWeatherMap API."""
        params["appid"] = self.api_key
        params["units"] = TEMPERATURE_UNIT
        params["lang"] = LANGUAGE
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise WeatherAPIError(f"API request failed: {str(e)}")
        except json.JSONDecodeError:
            raise WeatherAPIError("Invalid JSON response from API")
    
    @st.cache_data(ttl=CACHE_TTL)
    def get_current_weather(_self, city_name: str, lat: float = None, lon: float = None) -> Dict:
        """Get current weather data for a city."""
        if lat and lon:
            params = {"lat": lat, "lon": lon}
        else:
            params = {"q": f"{city_name},FR"}
        
        return _self._make_request("weather", params)
    
    @st.cache_data(ttl=CACHE_TTL)
    def get_forecast(_self, city_name: str, lat: float = None, lon: float = None) -> Dict:
        """Get 5-day weather forecast for a city."""
        if lat and lon:
            params = {"lat": lat, "lon": lon}
        else:
            params = {"q": f"{city_name},FR"}
        
        return _self._make_request("forecast", params)
    
    @st.cache_data(ttl=CACHE_TTL * 4)  # Cache historical data longer
    def get_historical_weather(_self, lat: float, lon: float, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get historical weather data (requires paid plan, using mock data for demo)."""
        # Note: Historical data requires paid OpenWeatherMap plan
        # For demo purposes, we'll generate mock historical data
        return _self._generate_mock_historical_data(lat, lon, start_date, end_date)
    
    def _generate_mock_historical_data(self, lat: float, lon: float, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Generate mock historical data for demonstration purposes."""
        import random
        import math
        
        data = []
        current_date = start_date
        base_temp = 15  # Base temperature for France
        
        while current_date <= end_date:
            # Simulate seasonal temperature variation
            day_of_year = current_date.timetuple().tm_yday
            seasonal_temp = base_temp + 10 * math.sin(2 * math.pi * (day_of_year - 80) / 365)
            
            # Add some random variation
            temp = seasonal_temp + random.uniform(-5, 5)
            humidity = random.randint(40, 90)
            pressure = random.randint(1000, 1025)
            
            data.append({
                "dt": int(current_date.timestamp()),
                "main": {
                    "temp": round(temp, 1),
                    "humidity": humidity,
                    "pressure": pressure
                },
                "weather": [{
                    "main": random.choice(["Clear", "Clouds", "Rain", "Snow"]),
                    "description": "mock data"
                }]
            })
            
            current_date += timedelta(days=1)
        
        return data
    
    @st.cache_data(ttl=CACHE_TTL)
    def get_multiple_cities_weather(_self, cities: List[Dict]) -> Dict[str, Dict]:
        """Get current weather for multiple cities."""
        weather_data = {}
        
        for city in cities:
            try:
                data = _self.get_current_weather(
                    city["name"], 
                    lat=city["lat"], 
                    lon=city["lon"]
                )
                weather_data[city["name"]] = data
            except WeatherAPIError as e:
                st.warning(f"Failed to fetch weather for {city['name']}: {str(e)}")
                continue
        
        return weather_data
    
    def get_weather_map_data(self, cities: List[Dict]) -> List[Dict]:
        """Get weather data formatted for map visualization."""
        map_data = []
        weather_data = self.get_multiple_cities_weather(cities)
        
        for city in cities:
            if city["name"] in weather_data:
                weather = weather_data[city["name"]]
                map_data.append({
                    "city": city["name"],
                    "lat": weather["coord"]["lat"],
                    "lon": weather["coord"]["lon"],
                    "temperature": weather["main"]["temp"],
                    "description": weather["weather"][0]["description"],
                    "humidity": weather["main"]["humidity"],
                    "pressure": weather["main"]["pressure"],
                    "wind_speed": weather.get("wind", {}).get("speed", 0)
                })
        
        return map_data


def format_weather_data(weather_data: Dict) -> Dict:
    """Format raw weather data for display."""
    return {
        "temperature": weather_data["main"]["temp"],
        "feels_like": weather_data["main"]["feels_like"],
        "humidity": weather_data["main"]["humidity"],
        "pressure": weather_data["main"]["pressure"],
        "description": weather_data["weather"][0]["description"].title(),
        "main": weather_data["weather"][0]["main"],
        "wind_speed": weather_data.get("wind", {}).get("speed", 0),
        "wind_direction": weather_data.get("wind", {}).get("deg", 0),
        "visibility": weather_data.get("visibility", 0) / 1000,  # Convert to km
        "city": weather_data["name"],
        "country": weather_data["sys"]["country"],
        "timestamp": datetime.fromtimestamp(weather_data["dt"])
    }
