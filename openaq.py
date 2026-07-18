"""
OpenAQ v3 fetcher — automated backup/primary source for historical
PM2.5 / AQI-relevant pollutant data (per Decision 5's fallback order).

Requires a free API key: https://explore.openaq.org/register
Set it as an env var: export OPENAQ_API_KEY="..."

Flow:
  1. find_locations() — search OpenAQ for monitoring locations near a
     station's lat/lon, so you don't have to hunt down location IDs by hand.
  2. fetch_measurements() — pull hourly PM2.5 (and other pollutants) for
     a given location ID and date range, paginating automatically.

Docs: https://docs.openaq.org/
"""

import os
import time
import pandas as pd
from common import get_json
import config
 
BASE_URL = "https://api.openaq.org/v3"
PM25_NAMES = {"pm25", "pm2.5", "pm2_5", "pm₂.₅"}
 
 
def _headers():
    key = os.environ.get(config.OPENAQ_API_KEY_ENV_VAR)
    if not key:
        raise EnvironmentError(
            f"Missing OpenAQ API key. Get a free one at "
            f"https://explore.openaq.org/register and run:\n"
            f'  export {config.OPENAQ_API_KEY_ENV_VAR}="your_key_here"'
        )
    return {"X-API-Key": key}
 
 
def find_locations(lat, lon, radius_m=5000, limit=10):
    """Search for OpenAQ monitoring locations near a point.
    Returns each location's sensors with their ids — v3 measurements are
    fetched per-sensor, not per-location, so the sensor id is what you
    actually need for fetch_measurements()."""
    params = {
        "coordinates": f"{lat},{lon}",
        "radius": radius_m,
        "limit": limit,
    }
    data = get_json(f"{BASE_URL}/locations", params, headers=_headers())
    results = data.get("results", [])
    out = []
    for r in results:
        out.append({
            "id": r.get("id"),
            "name": r.get("name"),
            "coordinates": r.get("coordinates"),
            "sensors": [
                {"id": s.get("id"), "parameter": s.get("parameter", {}).get("name")}
                for s in r.get("sensors", [])
            ],
        })
    return out


def is_pm25_sensor(sensor):
    name = str(sensor.get("parameter") or "").strip().lower()
    return name in PM25_NAMES


def choose_pm25_sensor(locations, keywords=None):
    keywords = [k.lower() for k in (keywords or [])]

    def score(location):
        name = str(location.get("name") or "").lower()
        return sum(1 for keyword in keywords if keyword in name)

    for loc in sorted(locations, key=score, reverse=True):
        match = next((sensor for sensor in loc["sensors"] if is_pm25_sensor(sensor)), None)
        if match:
            return loc, match
    return None, None
 
 
def fetch_measurements(sensor_id, start_date, end_date, station_name=""):
    """Pull historical hourly-average measurements for one sensor,
    paginating through all results. v3's /hours resource is the hourly
    average and is preferred over raw /measurements (same data when the
    upstream already reports hourly, per OpenAQ's own docs) — and it
    matches the hourly grain of the Open-Meteo weather data anyway.
    Returns a tidy hourly DataFrame."""
    all_rows = []
    page = 1
    limit = 1000
 
    print(f"Fetching OpenAQ sensor {sensor_id} for {station_name or sensor_id} "
          f"({start_date} to {end_date})...")
 
    while True:
        params = {
            "datetime_from": start_date,
            "datetime_to": end_date,
            "limit": limit,
            "page": page,
        }
        data = get_json(
            f"{BASE_URL}/sensors/{sensor_id}/hours", params, headers=_headers()
        )
        results = data.get("results", [])
        if not results:
            break
 
        for r in results:
            all_rows.append({
                "timestamp": r.get("period", {}).get("datetimeFrom", {}).get("utc"),
                "parameter": "pm25",
                "value": r.get("value"),
            })
 
        found = data.get("meta", {}).get("found", 0)
        if page * limit >= found or len(results) < limit:
            break
        page += 1
        time.sleep(0.3)  # be polite to the API
 
    df = pd.DataFrame(all_rows)
    if df.empty:
        print(f"  WARNING: no OpenAQ data returned for {station_name}")
        return df
 
    df["station"] = station_name
    return df
 
