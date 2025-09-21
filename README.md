# 🌦️ French Weather Analytics

A comprehensive weather dashboard for French cities built with Streamlit, providing real-time weather data, forecasts, and comparative analytics.

## Features

- **Real-time Weather Data**: Live weather conditions for major French cities
- **Multi-City Comparison**: Side-by-side weather comparisons with interactive charts
- **5-Day Forecast**: Detailed weather predictions with temperature trends
- **Interactive Dashboard**: Clean, responsive interface with dynamic visualizations
```
### Prerequisites
- Python 3.8+
- OpenWeatherMap API key (free at https://openweathermap.org/api)

### Local Installation

1. **Clone and setup environment**
```bash
git clone <repository-url>
cd Project-Weather
pip install -r requirements.txt
```

2. **Configure API key**
Create a `.env` file in the root directory getting inspired by the .env example :
```env
OPENWEATHER_API_KEY=your_api_key_here
```

3. **Launch application**
```bash
streamlit run src/app.py
```

The app will be available at `http://localhost:8501`

## Docker Deployment


### Using Docker directly
```bash
# Build the image
docker build -t weather-app .

# Run the container
docker run -p 8501:8501 --env-file .env weather-app
```

Access the application at `http://localhost:8501`

## Usage

1. **Select Cities**: Choose one or more French cities from the dropdown
2. **View Current Weather**: See real-time conditions including temperature, humidity, and weather descriptions
3. **Compare Cities**: Select multiple cities to view comparative weather data
4. **Forecast Analysis**: Navigate to the forecast section for 5-day predictions
5. **Interactive Charts**: Hover over charts for detailed information

## Project Structure

```
Project-Weather/
├── src/
│   ├── app.py                 # Main Streamlit application
│   ├── weather_api.py         # OpenWeatherMap API integration
│   ├── data_processor.py      # Data processing and formatting
│   ├── models.py             # Weather prediction models
│   └── config.py             # Application configuration
├── tests/
│   └── unit/                 # Unit test suite
├── requirements.txt          # Python dependencies
├── Dockerfile               # Container configuration
├── docker-compose.yml       # Multi-container setup
└── .env.example             # Environment variables template
```

## Development

### Running Tests
```bash
# Run all tests
pytest tests/

```

### Environment Variables
| Variable | Description | Required |
|----------|-------------|----------|
| `OPENWEATHER_API_KEY` | Your OpenWeatherMap API key | Yes |

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request
