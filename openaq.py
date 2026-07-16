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
    Returns a list of {id, name, distance} so you can pick the right one."""
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
            "parameters": [p.get("parameter", {}).get("name")
                            for p in r.get("sensors", [])],
        })
    return out


def fetch_measurements(location_id, start_date, end_date, parameter="pm25",
                        station_name=""):
    """Pull historical measurements for one location + parameter,
    paginating through all results. Returns a tidy hourly DataFrame."""
    all_rows = []
    page = 1
    limit = 1000

    print(f"Fetching OpenAQ '{parameter}' for {station_name or location_id} "
          f"({start_date} to {end_date})...")

    while True:
        params = {
            "date_from": start_date,
            "date_to": end_date,
            "limit": limit,
            "page": page,
        }
        data = get_json(
            f"{BASE_URL}/locations/{location_id}/measurements", params, headers=_headers()
        )
        results = data.get("results", [])
        if not results:
            break

        for r in results:
            all_rows.append({
                "timestamp": r.get("period", {}).get("datetimeFrom", {}).get("utc"),
                "parameter": r.get("parameter", {}).get("name", parameter),
                "value": r.get("value"),
                "unit": r.get("parameter", {}).get("units"),
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
    df = df[df["parameter"] == parameter]
    return df
