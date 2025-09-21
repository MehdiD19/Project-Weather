"""Configuration settings for the French Weather Analytics app."""

import os
from typing import Dict, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"

# Application Settings
CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))  # 5 minutes default
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# French Cities Configuration
FRENCH_CITIES: List[Dict[str, any]] = [
    {"name": "Paris", "lat": 48.8566, "lon": 2.3522},
    {"name": "Lyon", "lat": 45.7640, "lon": 4.8357},
    {"name": "Marseille", "lat": 43.2965, "lon": 5.3698},
    {"name": "Toulouse", "lat": 43.6047, "lon": 1.4442},
    {"name": "Nice", "lat": 43.7102, "lon": 7.2620},
    {"name": "Nantes", "lat": 47.2184, "lon": -1.5536},
    {"name": "Strasbourg", "lat": 48.5734, "lon": 7.7521},
    {"name": "Montpellier", "lat": 43.6110, "lon": 3.8767},
    {"name": "Bordeaux", "lat": 44.8378, "lon": -0.5792},
    {"name": "Lille", "lat": 50.6292, "lon": 3.0573},
    {"name": "Rennes", "lat": 48.1173, "lon": -1.6778},
    {"name": "Reims", "lat": 49.2583, "lon": 4.0317},
    {"name": "Saint-Étienne", "lat": 45.4397, "lon": 4.3872},
    {"name": "Le Havre", "lat": 49.4944, "lon": 0.1079},
    {"name": "Toulon", "lat": 43.1242, "lon": 5.9280}
]

# Streamlit Configuration
STREAMLIT_CONFIG = {
    "page_title": "French Weather Analytics",
    "page_icon": "🌦️",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Chart Configuration
CHART_THEME = "plotly_white"
CHART_HEIGHT = 400

# Data Processing Settings
TEMPERATURE_UNIT = "metric"  # metric, imperial, kelvin
LANGUAGE = "fr"  # French language for weather descriptions
