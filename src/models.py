"""Simple forecasting models for weather prediction."""

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta


class WeatherPredictor:
    """Simple weather prediction models."""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_processors = {}
    
    def prepare_features(self, df: pd.DataFrame) -> np.ndarray:
        """Prepare features for model training."""
        features = []
        
        # Time-based features
        if "datetime" in df.columns:
            df["day_of_year"] = df["datetime"].dt.dayofyear
            df["hour"] = df["datetime"].dt.hour
            df["month"] = df["datetime"].dt.month
            df["year"] = df["datetime"].dt.year
            
            # Cyclical features for seasonal patterns
            df["day_sin"] = np.sin(2 * np.pi * df["day_of_year"] / 365.25)
            df["day_cos"] = np.cos(2 * np.pi * df["day_of_year"] / 365.25)
            df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
            df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)
            
            features.extend(["day_sin", "day_cos", "hour_sin", "hour_cos"])
        
        # Lag features (previous values)
        if "temperature" in df.columns:
            df["temp_lag_1"] = df["temperature"].shift(1)
            df["temp_lag_7"] = df["temperature"].shift(7) if len(df) > 7 else df["temperature"].shift(1)
            features.extend(["temp_lag_1", "temp_lag_7"])
        
        # Additional weather features
        weather_features = ["humidity", "pressure", "wind_speed"]
        for feature in weather_features:
            if feature in df.columns:
                features.append(feature)
        
        # Remove rows with NaN values
        feature_df = df[features].dropna()
        return feature_df
    
    def train_temperature_model(self, df: pd.DataFrame, model_type: str = "linear") -> Dict:
        """Train a temperature prediction model."""
        if len(df) < 10:
            raise ValueError("Insufficient data for training (need at least 10 samples)")
        
        # Prepare features and target
        feature_df = self.prepare_features(df.copy())
        
        if feature_df.empty:
            raise ValueError("No valid features could be created from the data")
        
        # Align target with features (handle lag features)
        target_indices = feature_df.index
        y = df.loc[target_indices, "temperature"].values
        X = feature_df.values
        
        # Split data (80% train, 20% test)
        split_idx = int(0.8 * len(X))
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        # Train model
        if model_type == "polynomial":
            poly_features = PolynomialFeatures(degree=2, include_bias=False)
            X_train_poly = poly_features.fit_transform(X_train)
            X_test_poly = poly_features.transform(X_test)
            
            model = LinearRegression()
            model.fit(X_train_poly, y_train)
            
            y_pred = model.predict(X_test_poly)
            self.feature_processors["temperature"] = poly_features
        else:
            model = LinearRegression()
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
        
        # Store model
        self.models["temperature"] = model
        
        # Calculate metrics
        metrics = {
            "mae": mean_absolute_error(y_test, y_pred),
            "mse": mean_squared_error(y_test, y_pred),
            "rmse": np.sqrt(mean_squared_error(y_test, y_pred)),
            "r2": r2_score(y_test, y_pred),
            "model_type": model_type,
            "n_features": X.shape[1],
            "n_samples": len(X)
        }
        
        return metrics
    
    def predict_temperature(self, df: pd.DataFrame, days_ahead: int = 7) -> Tuple[List[float], List[datetime], Dict]:
        """Predict future temperatures."""
        if "temperature" not in self.models:
            raise ValueError("Temperature model not trained yet")
        
        model = self.models["temperature"]
        
        # Prepare the last known data point
        last_data = df.tail(10).copy()  # Use last 10 points for context
        
        predictions = []
        prediction_dates = []
        
        # Get the last date
        last_date = df["datetime"].iloc[-1]
        
        for i in range(days_ahead):
            # Create future date
            future_date = last_date + timedelta(days=i+1)
            prediction_dates.append(future_date)
            
            # Create a row for prediction
            future_row = last_data.iloc[-1:].copy()
            future_row["datetime"] = future_date
            
            # Prepare features
            feature_df = self.prepare_features(future_row)
            
            if feature_df.empty:
                # Fallback: use simple trend
                trend = df["temperature"].tail(7).diff().mean()
                pred = df["temperature"].iloc[-1] + trend * (i + 1)
            else:
                X = feature_df.values
                
                # Apply polynomial features if used
                if "temperature" in self.feature_processors:
                    X = self.feature_processors["temperature"].transform(X)
                
                pred = model.predict(X)[0]
            
            predictions.append(pred)
            
            # Update last_data with prediction for next iteration
            new_row = last_data.iloc[-1:].copy()
            new_row["temperature"] = pred
            new_row["datetime"] = future_date
            last_data = pd.concat([last_data.tail(9), new_row], ignore_index=True)
        
        # Calculate prediction confidence (simple approach)
        recent_temps = df["temperature"].tail(30)
        confidence = {
            "std_dev": recent_temps.std(),
            "mean_temp": recent_temps.mean(),
            "confidence_interval_95": 1.96 * recent_temps.std()
        }
        
        return predictions, prediction_dates, confidence
    
    def simple_moving_average_prediction(self, df: pd.DataFrame, window: int = 7, days_ahead: int = 7) -> Tuple[List[float], List[datetime]]:
        """Simple moving average prediction."""
        if len(df) < window:
            window = len(df)
        
        # Calculate moving average
        recent_temps = df["temperature"].tail(window)
        avg_temp = recent_temps.mean()
        
        # Simple trend calculation
        trend = recent_temps.diff().mean()
        
        predictions = []
        prediction_dates = []
        last_date = df["datetime"].iloc[-1]
        
        for i in range(days_ahead):
            future_date = last_date + timedelta(days=i+1)
            pred_temp = avg_temp + trend * (i + 1)
            
            predictions.append(pred_temp)
            prediction_dates.append(future_date)
        
        return predictions, prediction_dates
    
    def seasonal_naive_prediction(self, df: pd.DataFrame, days_ahead: int = 7) -> Tuple[List[float], List[datetime]]:
        """Seasonal naive prediction (use same day last week/year)."""
        predictions = []
        prediction_dates = []
        last_date = df["datetime"].iloc[-1]
        
        for i in range(days_ahead):
            future_date = last_date + timedelta(days=i+1)
            prediction_dates.append(future_date)
            
            # Try to find same day of week from previous week
            week_ago = future_date - timedelta(weeks=1)
            similar_day = df[df["datetime"].dt.date == week_ago.date()]
            
            if not similar_day.empty:
                pred_temp = similar_day["temperature"].mean()
            else:
                # Fallback to same day of year from previous year
                year_ago = future_date.replace(year=future_date.year - 1)
                try:
                    similar_day = df[df["datetime"].dt.date == year_ago.date()]
                    if not similar_day.empty:
                        pred_temp = similar_day["temperature"].mean()
                    else:
                        # Final fallback: overall average
                        pred_temp = df["temperature"].mean()
                except ValueError:
                    pred_temp = df["temperature"].mean()
            
            predictions.append(pred_temp)
        
        return predictions, prediction_dates
    
    def get_model_performance(self) -> Dict:
        """Get performance metrics of trained models."""
        if not self.models:
            return {"error": "No models trained yet"}
        
        performance = {}
        for model_name, model in self.models.items():
            if hasattr(model, "score"):
                # This is a simple placeholder - in practice you'd want to store
                # validation metrics from training
                performance[model_name] = {
                    "model_type": type(model).__name__,
                    "features_count": getattr(model, "n_features_in_", "unknown")
                }
        
        return performance
