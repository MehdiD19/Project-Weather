"""Tests for data processing."""

import pytest
import pandas as pd
from datetime import datetime
from data_processor import WeatherDataProcessor


def test_process_weather_data():
    """Test basic weather data processing."""
    processor = WeatherDataProcessor()
    
    weather_data = {
        "Paris": {
            "main": {"temp": 20.5, "feels_like": 19.8, "humidity": 65, "pressure": 1013},
            "weather": [{"description": "clear sky"}],
            "wind": {"speed": 3.5},
            "dt": int(datetime.now().timestamp())
        }
    }
    
    df = processor.process_current_weather(weather_data)
    
    assert len(df) == 1
    assert df.iloc[0]["city"] == "Paris"
    assert df.iloc[0]["temperature"] == 20.5


def test_temperature_stats():
    """Test temperature statistics."""
    processor = WeatherDataProcessor()
    
    df = pd.DataFrame({
        'temperature': [20, 22, 18, 25, 19]
    })
    
    stats = processor.calculate_temperature_statistics(df)
    
    assert "mean" in stats
    assert "max" in stats
    assert "min" in stats
    assert stats["max"] == 25
    assert stats["min"] == 18
