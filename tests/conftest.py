"""Test configuration."""

import pytest
import pandas as pd
from datetime import datetime
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.fixture
def mock_weather_response():
    """Mock weather API response."""
    return {
        "coord": {"lon": 2.3522, "lat": 48.8566},
        "weather": [{"main": "Clear", "description": "clear sky"}],
        "main": {
            "temp": 20.5,
            "feels_like": 19.8,
            "pressure": 1013,
            "humidity": 65
        },
        "wind": {"speed": 3.5, "deg": 270},
        "dt": int(datetime.now().timestamp()),
        "sys": {"country": "FR"},
        "name": "Paris"
    }


@pytest.fixture 
def sample_weather_data():
    """Sample weather data for testing."""
    return pd.DataFrame({
        'city': ['Paris', 'Lyon'],
        'temperature': [20.5, 18.2],
        'humidity': [65, 70]
    })
