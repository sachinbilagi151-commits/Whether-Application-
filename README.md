# Weather Application (Python)

A command-line weather app built with Python and the OpenWeatherMap API.

## Features

- Search weather by city
- Display current temperature (plus feels-like, humidity, wind)
- Display 5-day forecast (daily min/max temperature)
- Display weather condition (e.g. "Light Rain", "Clear Sky")
- Display sunrise and sunset times (in the city's local time)
- Metric (°C) or imperial (°F) units
- Friendly errors for invalid city, bad API key, no internet, and rate limits

## Project Structure

```
weather_app/
├── weather_app.py      # Application source code
├── requirements.txt    # Python dependencies
├── .env.example        # Template for your API key
└── README.md           # This file
```

## Requirements

- Python 3.8+
- A free OpenWeatherMap API key

## Setup

1. **Get an API key**
   Sign up at https://openweathermap.org/api and copy your key from the
   "API keys" tab. New keys can take up to a couple of hours to activate.

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your key** (choose one)

   - Create a `.env` file:
     ```bash
     cp .env.example .env
     # then edit .env and paste your key
     ```
   - Or set an environment variable:
     ```bash
     export OPENWEATHER_API_KEY="your_key_here"        # macOS / Linux
     setx OPENWEATHER_API_KEY "your_key_here"          # Windows (restart terminal)
     ```

## Usage

**Interactive mode**
```bash
python weather_app.py
```
Type a city name at the prompt; enter `q` to quit.

**One-shot mode**
```bash
python weather_app.py London
python weather_app.py "New York"
python weather_app.py Paris,FR
python weather_app.py Chicago --units imperial
```

## Sample Output

```
==================================================
 Weather in London, GB
==================================================
 Temperature : 14.2°C (feels like 13.5°C)
 Condition   : Light Rain
 Humidity    : 82%
 Wind        : 4.1 m/s
 Sunrise     : 07:12 AM
 Sunset      : 06:08 PM

--------------------------------------------------
 5-Day Forecast
--------------------------------------------------
 Date             Min     Max  Condition
 Fri, 09 Oct     11.0C   15.2C  Light Rain
 Sat, 10 Oct      9.8C   14.0C  Broken Clouds
 ...
```

(Values above are illustrative.)

## How It Works

| Feature | API endpoint |
|---|---|
| Current temperature, condition, sunrise/sunset | `/data/2.5/weather` |
| 5-day forecast | `/data/2.5/forecast` (3-hour steps, grouped per day in code) |

The forecast endpoint returns 40 three-hour entries. The app groups them by
the city's local date and calculates the daily minimum, maximum, and most
common weather condition. The first row may be a partial day (today).

## Troubleshooting

| Message | Fix |
|---|---|
| `Missing API key` | Set `OPENWEATHER_API_KEY` or create `.env` |
| `Invalid API key` | Check the key; wait for new keys to activate |
| `City not found` | Check spelling or add a country code (`Paris,FR`) |
| `Network error` | Check your internet connection |

## Ideas for Extension

- Tkinter or Flask web interface
- Weather icons
- Save favorite cities
- Search by coordinates or zip code
- Hourly forecast and air quality data

## License

Free to use and modify for learning and personal projects.
