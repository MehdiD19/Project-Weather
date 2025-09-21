"""Tests for weather API."""

import pytest
from unittest.mock import Mock, patch
from weather_api import WeatherAPI, WeatherAPIError


def test_api_init_without_key():
    """Test API fails without key."""
    with patch('weather_api.OPENWEATHER_API_KEY', None):
        with pytest.raises(WeatherAPIError):
            WeatherAPI()


@patch('weather_api.OPENWEATHER_API_KEY', 'test_key')
def test_api_init_with_key():
    """Test API works with key."""
    api = WeatherAPI()
    assert api.api_key == 'test_key'


@patch('weather_api.OPENWEATHER_API_KEY', 'test_key')
def test_api_request(mock_weather_response):
    """Test API request works."""
    with patch('requests.Session.get') as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = mock_weather_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        api = WeatherAPI()
        result = api._make_request("weather", {"q": "Paris"})
        
        assert result["name"] == "Paris"
