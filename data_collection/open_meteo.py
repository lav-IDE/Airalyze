"""
Open-Meteo weather fetcher.

Fully automated, no API key required, free for non-commercial use.
Two calls per station:
  1. Archive API  -> actual historical weather (for training features)
  2. Forecast API -> the next N days (for real-time inference / demo)

Docs: https://open-meteo.com/en/docs/historical-weather-api
"""

import pandas as pd
from .common import get_json

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

HOURLY_VARS = [
    "temperature_2m",
    "relative_humidity_2m",
    "wind_speed_10m",
    "wind_direction_10m",
    "surface_pressure",
]


def fetch_historical_weather(lat, lon, start_date, end_date, station_name=""):
    """Returns an hourly DataFrame of actual historical weather."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": ",".join(HOURLY_VARS),
        "timezone": "Asia/Kolkata",
    }
    print(f"Fetching historical weather for {station_name or (lat, lon)} "
          f"({start_date} to {end_date})...")
    data = get_json(ARCHIVE_URL, params)

    hourly = data.get("hourly", {})
    df = pd.DataFrame(hourly)
    if df.empty:
        print(f"  WARNING: no data returned for {station_name}")
        return df

    df.rename(columns={
        "time": "timestamp",
        "temperature_2m": "temp",
        "relative_humidity_2m": "humidity",
        "wind_speed_10m": "wind_speed",
        "wind_direction_10m": "wind_dir_deg",
        "surface_pressure": "pressure",
    }, inplace=True)
    df["station"] = station_name
    return df


def fetch_forecast_weather(lat, lon, station_name="", forecast_days=3):
    """Returns forecasted (not actual) weather — use this at inference time
    to avoid the actual-vs-forecast leakage risk flagged in Decision 7."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ",".join(HOURLY_VARS),
        "forecast_days": forecast_days,
        "timezone": "Asia/Kolkata",
    }
    print(f"Fetching {forecast_days}-day forecast weather for "
          f"{station_name or (lat, lon)}...")
    data = get_json(FORECAST_URL, params)

    hourly = data.get("hourly", {})
    df = pd.DataFrame(hourly)
    if df.empty:
        return df

    df.rename(columns={
        "time": "timestamp",
        "temperature_2m": "temp_forecast",
        "relative_humidity_2m": "humidity_forecast",
        "wind_speed_10m": "wind_speed_forecast",
        "wind_direction_10m": "wind_dir_deg_forecast",
        "surface_pressure": "pressure_forecast",
    }, inplace=True)
    df["station"] = station_name
    return df


def add_circular_wind_encoding(df, deg_col="wind_dir_deg"):
    """Adds wind_dir_sin / wind_dir_cos per the confirmed feature set
    in Decision 7 (circular encoding, not raw degrees)."""
    import numpy as np
    if deg_col not in df.columns:
        return df
    radians = np.deg2rad(df[deg_col])
    df["wind_dir_sin"] = np.sin(radians)
    df["wind_dir_cos"] = np.cos(radians)
    return df
