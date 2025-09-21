"""Data processing and analysis functions for weather data."""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import mean_squared_error, r2_score


class WeatherDataProcessor:
    """Process and analyze weather data."""
    
    def __init__(self):
        self.data_cache = {}
    
    def process_current_weather(self, weather_data: Dict[str, Dict]) -> pd.DataFrame:
        """Convert current weather data to DataFrame."""
        processed_data = []
        
        for city_name, data in weather_data.items():
            processed_data.append({
                "city": city_name,
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "description": data["weather"][0]["description"],
                "wind_speed": data.get("wind", {}).get("speed", 0),
                "visibility": data.get("visibility", 0) / 1000,  # Convert to km
                "timestamp": datetime.fromtimestamp(data["dt"])
            })
        
        return pd.DataFrame(processed_data)
    
    def process_forecast_data(self, forecast_data: Dict) -> pd.DataFrame:
        """Convert forecast data to DataFrame."""
        forecast_list = []
        
        for item in forecast_data["list"]:
            forecast_list.append({
                "datetime": datetime.fromtimestamp(item["dt"]),
                "temperature": item["main"]["temp"],
                "feels_like": item["main"]["feels_like"],
                "humidity": item["main"]["humidity"],
                "pressure": item["main"]["pressure"],
                "description": item["weather"][0]["description"],
                "wind_speed": item.get("wind", {}).get("speed", 0),
                "precipitation": item.get("rain", {}).get("3h", 0) + item.get("snow", {}).get("3h", 0)
            })
        
        df = pd.DataFrame(forecast_list)
        df["date"] = df["datetime"].dt.date
        df["hour"] = df["datetime"].dt.hour
        
        return df
    
    def process_historical_data(self, historical_data: List[Dict]) -> pd.DataFrame:
        """Convert historical data to DataFrame."""
        processed_data = []
        
        for item in historical_data:
            processed_data.append({
                "datetime": datetime.fromtimestamp(item["dt"]),
                "temperature": item["main"]["temp"],
                "humidity": item["main"]["humidity"],
                "pressure": item["main"]["pressure"],
                "description": item["weather"][0]["description"]
            })
        
        df = pd.DataFrame(processed_data)
        df["date"] = df["datetime"].dt.date
        df["month"] = df["datetime"].dt.month
        df["year"] = df["datetime"].dt.year
        df["day_of_year"] = df["datetime"].dt.dayofyear
        
        return df
    
    def calculate_temperature_statistics(self, df: pd.DataFrame) -> Dict:
        """Calculate temperature statistics."""
        temp_stats = {
            "mean": df["temperature"].mean(),
            "median": df["temperature"].median(),
            "std": df["temperature"].std(),
            "min": df["temperature"].min(),
            "max": df["temperature"].max(),
            "range": df["temperature"].max() - df["temperature"].min()
        }
        
        return temp_stats
    
    def detect_temperature_trends(self, df: pd.DataFrame) -> Dict:
        """Detect temperature trends in the data."""
        if len(df) < 2:
            return {"trend": "insufficient_data", "slope": 0, "r2": 0}
        
        # Prepare data for linear regression
        df_sorted = df.sort_values("datetime")
        X = np.arange(len(df_sorted)).reshape(-1, 1)
        y = df_sorted["temperature"].values
        
        # Fit linear regression
        model = LinearRegression()
        model.fit(X, y)
        
        # Calculate predictions and metrics
        y_pred = model.predict(X)
        r2 = r2_score(y, y_pred)
        slope = model.coef_[0]
        
        # Determine trend direction
        if abs(slope) < 0.01:
            trend = "stable"
        elif slope > 0:
            trend = "increasing"
        else:
            trend = "decreasing"
        
        return {
            "trend": trend,
            "slope": slope,
            "r2": r2,
            "slope_per_day": slope  # Since X is in days
        }
    
    def simple_temperature_forecast(self, df: pd.DataFrame, days_ahead: int = 7) -> Tuple[List[float], List[datetime]]:
        """Simple linear regression forecast for temperature."""
        if len(df) < 5:
            raise ValueError("Insufficient data for forecasting (need at least 5 data points)")
        
        # Prepare data
        df_sorted = df.sort_values("datetime")
        X = np.arange(len(df_sorted)).reshape(-1, 1)
        y = df_sorted["temperature"].values
        
        # Fit model with polynomial features for better fit
        poly_features = PolynomialFeatures(degree=2)
        X_poly = poly_features.fit_transform(X)
        
        model = LinearRegression()
        model.fit(X_poly, y)
        
        # Generate future dates
        last_date = df_sorted["datetime"].iloc[-1]
        future_dates = [last_date + timedelta(days=i) for i in range(1, days_ahead + 1)]
        
        # Generate predictions
        future_X = np.arange(len(df_sorted), len(df_sorted) + days_ahead).reshape(-1, 1)
        future_X_poly = poly_features.transform(future_X)
        future_temps = model.predict(future_X_poly)
        
        return future_temps.tolist(), future_dates
    
    def analyze_seasonal_patterns(self, df: pd.DataFrame) -> Dict:
        """Analyze seasonal patterns in weather data."""
        if "month" not in df.columns:
            df["month"] = df["datetime"].dt.month
        
        monthly_stats = df.groupby("month")["temperature"].agg([
            "mean", "std", "min", "max"
        ]).round(2)
        
        seasonal_analysis = {
            "monthly_averages": monthly_stats.to_dict(),
            "warmest_month": monthly_stats["mean"].idxmax(),
            "coldest_month": monthly_stats["mean"].idxmin(),
            "most_variable_month": monthly_stats["std"].idxmax(),
            "temperature_range_by_month": (monthly_stats["max"] - monthly_stats["min"]).to_dict()
        }
        
        return seasonal_analysis
    
    def compare_cities_temperature(self, current_weather_df: pd.DataFrame) -> Dict:
        """Compare temperature across different cities."""
        if current_weather_df.empty:
            return {}
        
        comparison = {
            "warmest_city": current_weather_df.loc[current_weather_df["temperature"].idxmax(), "city"],
            "coldest_city": current_weather_df.loc[current_weather_df["temperature"].idxmin(), "city"],
            "temperature_range": current_weather_df["temperature"].max() - current_weather_df["temperature"].min(),
            "average_temperature": current_weather_df["temperature"].mean(),
            "cities_above_average": current_weather_df[
                current_weather_df["temperature"] > current_weather_df["temperature"].mean()
            ]["city"].tolist()
        }
        
        return comparison
    
    def calculate_comfort_index(self, temperature: float, humidity: float, wind_speed: float) -> Tuple[float, str]:
        """Calculate a simple comfort index based on temperature, humidity, and wind."""
        # Simple comfort calculation (Heat Index approximation)
        if temperature < 10:
            comfort_score = max(0, 50 - (10 - temperature) * 5)
            comfort_level = "Cold"
        elif temperature > 30:
            # Factor in humidity for hot weather
            heat_index = temperature + 0.4 * (humidity - 50)
            comfort_score = max(0, 100 - (heat_index - 25) * 3)
            comfort_level = "Hot" if comfort_score < 70 else "Warm"
        else:
            # Comfortable temperature range
            base_comfort = 85
            temp_penalty = abs(temperature - 20) * 2
            humidity_penalty = abs(humidity - 60) * 0.5
            wind_bonus = min(wind_speed * 2, 10)  # Light wind is comfortable
            
            comfort_score = base_comfort - temp_penalty - humidity_penalty + wind_bonus
            comfort_score = max(0, min(100, comfort_score))
            
            if comfort_score >= 80:
                comfort_level = "Very Comfortable"
            elif comfort_score >= 65:
                comfort_level = "Comfortable"
            elif comfort_score >= 50:
                comfort_level = "Moderate"
            else:
                comfort_level = "Uncomfortable"
        
        return round(comfort_score, 1), comfort_level
