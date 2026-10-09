#!/usr/bin/env python3
"""
Weather Application
-------------------
Features:
  * Search weather by city
  * Display current temperature
  * Display 5-day forecast
  * Display weather condition
  * Display sunrise and sunset

Data source: OpenWeatherMap (https://openweathermap.org/api)
"""

import argparse
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

import requests

BASE_URL = "https://api.openweathermap.org/data/2.5"
TIMEOUT = 10  # seconds

UNITS = {
    "metric": {"temp": "°C", "speed": "m/s"},
    "imperial": {"temp": "°F", "speed": "mph"},
}


class WeatherError(Exception):
    """Raised for any user-facing weather lookup problem."""


# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------
def load_env_file(path: str = ".env") -> None:
    """Minimal .env loader (KEY=VALUE per line) so no extra package is needed."""
    if not os.path.isfile(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def get_api_key() -> str:
    load_env_file()
    key = os.environ.get("OPENWEATHER_API_KEY")
    if not key:
        raise WeatherError(
            "Missing API key. Set OPENWEATHER_API_KEY as an environment "
            "variable or in a .env file (see README.md)."
        )
    return key


# --------------------------------------------------------------------------
# API calls
# --------------------------------------------------------------------------
def fetch(endpoint: str, city: str, api_key: str, units: str) -> dict:
    """Call an OpenWeatherMap endpoint and return parsed JSON."""
    params = {"q": city, "appid": api_key, "units": units}
    try:
        resp = requests.get(f"{BASE_URL}/{endpoint}", params=params, timeout=TIMEOUT)
    except requests.exceptions.ConnectionError:
        raise WeatherError("Network error. Please check your internet connection.")
    except requests.exceptions.Timeout:
        raise WeatherError("The weather service timed out. Try again shortly.")
    except requests.exceptions.RequestException as exc:
        raise WeatherError(f"Request failed: {exc}")

    if resp.status_code == 200:
        return resp.json()
    if resp.status_code == 404:
        raise WeatherError(f"City '{city}' not found. Check the spelling.")
    if resp.status_code == 401:
        raise WeatherError("Invalid API key (new keys can take a couple of hours to activate).")
    if resp.status_code == 429:
        raise WeatherError("API rate limit reached. Please wait and try again.")
    raise WeatherError(f"Weather service error (HTTP {resp.status_code}).")


def get_current_weather(city: str, api_key: str, units: str) -> dict:
    return fetch("weather", city, api_key, units)


def get_forecast(city: str, api_key: str, units: str) -> dict:
    return fetch("forecast", city, api_key, units)


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def to_local(ts: int, tz_offset: int) -> datetime:
    """Convert a UTC unix timestamp to the city's local time."""
    return datetime.fromtimestamp(ts, tz=timezone(timedelta(seconds=tz_offset)))


def summarize_forecast(forecast: dict, days: int = 5) -> list:
    """
    The API returns 3-hourly entries. Group them by local date and
    compute min/max temperature and the most common condition per day.
    """
    tz_offset = forecast["city"]["timezone"]
    grouped = defaultdict(list)
    for entry in forecast["list"]:
        local_dt = to_local(entry["dt"], tz_offset)
        grouped[local_dt.date()].append(entry)

    summary = []
    for date in sorted(grouped)[:days]:
        entries = grouped[date]
        temps = [e["main"]["temp"] for e in entries]
        conditions = Counter(e["weather"][0]["description"] for e in entries)
        humidity = sum(e["main"]["humidity"] for e in entries) / len(entries)
        summary.append(
            {
                "date": date,
                "min": min(temps),
                "max": max(temps),
                "condition": conditions.most_common(1)[0][0].title(),
                "humidity": round(humidity),
            }
        )
    return summary


# --------------------------------------------------------------------------
# Display
# --------------------------------------------------------------------------
def display_current(data: dict, units: str) -> None:
    u = UNITS[units]
    tz = data["timezone"]
    sunrise = to_local(data["sys"]["sunrise"], tz).strftime("%I:%M %p")
    sunset = to_local(data["sys"]["sunset"], tz).strftime("%I:%M %p")
    condition = data["weather"][0]["description"].title()

    print("=" * 50)
    print(f" Weather in {data['name']}, {data['sys'].get('country', '')}")
    print("=" * 50)
    print(f" Temperature : {data['main']['temp']:.1f}{u['temp']} "
          f"(feels like {data['main']['feels_like']:.1f}{u['temp']})")
    print(f" Condition   : {condition}")
    print(f" Humidity    : {data['main']['humidity']}%")
    print(f" Wind        : {data['wind']['speed']} {u['speed']}")
    print(f" Sunrise     : {sunrise}")
    print(f" Sunset      : {sunset}")


def display_forecast(summary: list, units: str) -> None:
    u = UNITS[units]
    print()
    print("-" * 50)
    print(" 5-Day Forecast")
    print("-" * 50)
    print(f" {'Date':<14}{'Min':>8}{'Max':>8}  Condition")
    for day in summary:
        label = day["date"].strftime("%a, %d %b")
        print(f" {label:<14}{day['min']:>6.1f}{u['temp'][-1]}"
              f"{day['max']:>6.1f}{u['temp'][-1]}  {day['condition']}")
    print()


def show_weather(city: str, api_key: str, units: str) -> None:
    current = get_current_weather(city, api_key, units)
    forecast = get_forecast(city, api_key, units)
    display_current(current, units)
    display_forecast(summarize_forecast(forecast), units)


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Search weather by city.")
    parser.add_argument("city", nargs="*", help="City name, e.g. London or 'Paris,FR'")
    parser.add_argument(
        "-u", "--units", choices=UNITS.keys(), default="metric",
        help="metric (°C) or imperial (°F). Default: metric",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        api_key = get_api_key()
    except WeatherError as exc:
        print(f"Error: {exc}")
        return 1

    # One-shot mode: python weather_app.py London
    if args.city:
        try:
            show_weather(" ".join(args.city), api_key, args.units)
            return 0
        except WeatherError as exc:
            print(f"Error: {exc}")
            return 1

    # Interactive mode
    print("Weather App — type a city name (or 'q' to quit).")
    while True:
        try:
            city = input("\nCity: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            return 0
        if city.lower() in {"q", "quit", "exit"}:
            print("Goodbye!")
            return 0
        if not city:
            continue
        try:
            show_weather(city, api_key, args.units)
        except WeatherError as exc:
            print(f"Error: {exc}")


if __name__ == "__main__":
    sys.exit(main())
