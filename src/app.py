"""Main Streamlit application for French Weather Analytics."""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

try:
    from .config import STREAMLIT_CONFIG, FRENCH_CITIES, CHART_THEME, CHART_HEIGHT
    from .weather_api import WeatherAPI, WeatherAPIError, format_weather_data
    from .data_processor import WeatherDataProcessor
    from .models import WeatherPredictor
except ImportError:
    from config import STREAMLIT_CONFIG, FRENCH_CITIES, CHART_THEME, CHART_HEIGHT
    from weather_api import WeatherAPI, WeatherAPIError, format_weather_data
    from data_processor import WeatherDataProcessor
    from models import WeatherPredictor


# Page configuration
st.set_page_config(**STREAMLIT_CONFIG)

# Initialize session state
if "weather_api" not in st.session_state:
    try:
        st.session_state.weather_api = WeatherAPI()
    except WeatherAPIError as e:
        st.error(f"Failed to initialize Weather API: {e}")
        st.stop()

if "data_processor" not in st.session_state:
    st.session_state.data_processor = WeatherDataProcessor()


def main():
    """Main application function."""
    st.title("🌦️ French Weather Analytics")
    st.markdown("Real-time weather data and analysis for French cities")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Choose a page", [
        "🏠 Dashboard", 
        "📊 City Comparison", 
        "📈 Simple Forecast"
    ])
    
    # Route to different pages
    if page == "🏠 Dashboard":
        dashboard_page()
    elif page == "📊 City Comparison":
        comparison_page()
    elif page == "📈 Simple Forecast":
        forecast_page()


def dashboard_page():
    """Main dashboard with current weather overview."""
    st.header("Current Weather Overview")
    
    # City selection
    selected_cities = st.multiselect(
        "Select French cities:",
        options=[city["name"] for city in FRENCH_CITIES],
        default=["Paris", "Lyon", "Marseille", "Nice"]
    )
    
    if not selected_cities:
        st.warning("Please select at least one city.")
        return
    
    # Filter selected cities
    cities_data = [city for city in FRENCH_CITIES if city["name"] in selected_cities]
    
    # Fetch weather data
    with st.spinner("Loading weather data..."):
        try:
            weather_data = st.session_state.weather_api.get_multiple_cities_weather(cities_data)
            current_df = st.session_state.data_processor.process_current_weather(weather_data)
            
            if current_df.empty:
                st.error("No weather data available.")
                return
            
        except Exception as e:
            st.error(f"Error fetching weather data: {e}")
            return
    
    # Display weather cards
    cols = st.columns(min(len(selected_cities), 3))
    for idx, city in enumerate(selected_cities):
        if city in weather_data:
            with cols[idx % 3]:
                display_weather_card(weather_data[city])
    
    # Temperature comparison chart
    st.subheader("Temperature Comparison")
    fig = px.bar(
        current_df,
        x="city",
        y="temperature",
        title="Current Temperature by City",
        color="temperature",
        color_continuous_scale="RdYlBu_r"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Average Temperature", f"{current_df['temperature'].mean():.1f}°C")
    with col2:
        warmest = current_df.loc[current_df['temperature'].idxmax()]
        st.metric("Warmest City", warmest['city'])
    with col3:
        coldest = current_df.loc[current_df['temperature'].idxmin()]
        st.metric("Coldest City", coldest['city'])


def display_weather_card(weather_data):
    """Display a weather card for a single city."""
    formatted_data = format_weather_data(weather_data)
    
    st.markdown(f"""
    **{formatted_data['city']}**
    
    🌡️ **{formatted_data['temperature']:.1f}°C**
    
    {formatted_data['description']}
    
    💧 Humidity: {formatted_data['humidity']}%
    
    💨 Wind: {formatted_data['wind_speed']:.1f} m/s
    """)


def comparison_page():
    """City comparison analysis."""
    st.header("City Weather Comparison")
    
    selected_cities = st.multiselect(
        "Select cities to compare:",
        options=[city["name"] for city in FRENCH_CITIES],
        default=["Paris", "Lyon", "Nice"]
    )
    
    if len(selected_cities) < 2:
        st.warning("Please select at least 2 cities for comparison.")
        return
    
    cities_data = [city for city in FRENCH_CITIES if city["name"] in selected_cities]
    
    with st.spinner("Loading weather data..."):
        weather_data = st.session_state.weather_api.get_multiple_cities_weather(cities_data)
        current_df = st.session_state.data_processor.process_current_weather(weather_data)
    
    # Multi-metric comparison
    metrics = ["temperature", "humidity", "pressure", "wind_speed"]
    
    for metric in metrics:
        if metric in current_df.columns:
            fig = px.bar(
                current_df,
                x="city",
                y=metric,
                title=f"{metric.replace('_', ' ').title()} by City"
            )
            st.plotly_chart(fig, use_container_width=True)


def forecast_page():
    """Simple weather forecasting."""
    st.header("5-Day Weather Forecast")
    
    selected_city = st.selectbox(
        "Select a city:",
        options=[city["name"] for city in FRENCH_CITIES]
    )
    
    city_data = next((city for city in FRENCH_CITIES if city["name"] == selected_city), None)
    
    with st.spinner("Loading forecast..."):
        try:
            forecast_data = st.session_state.weather_api.get_forecast(
                selected_city, city_data["lat"], city_data["lon"]
            )
            forecast_df = st.session_state.data_processor.process_forecast_data(forecast_data)
            
            # Display forecast chart
            fig = px.line(
                forecast_df,
                x="datetime",
                y="temperature",
                title=f"5-Day Temperature Forecast - {selected_city}"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Forecast table
            st.subheader("Detailed Forecast")
            display_df = forecast_df[["datetime", "temperature", "humidity", "description"]].round(1)
            st.dataframe(display_df, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error loading forecast: {e}")


if __name__ == "__main__":
    main()