"""Tests for prediction models."""

import pytest
import pandas as pd
from datetime import datetime
from models import WeatherPredictor


def test_predictor_init():
    """Test predictor creation."""
    predictor = WeatherPredictor()
    
    assert hasattr(predictor, 'models')
    assert isinstance(predictor.models, dict)


def test_moving_average():
    """Test simple moving average prediction."""
    predictor = WeatherPredictor()
    
    df = pd.DataFrame({
        'datetime': pd.date_range('2024-01-01', periods=10, freq='D'),
        'temperature': [20, 22, 18, 25, 19, 21, 23, 17, 24, 20]
    })
    
    predictions, dates = predictor.simple_moving_average_prediction(df, days_ahead=3)
    
    assert len(predictions) == 3
    assert len(dates) == 3
    assert all(isinstance(pred, (int, float)) for pred in predictions)
