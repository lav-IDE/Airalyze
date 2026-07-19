from pathlib import Path

import pandas as pd

from . import cpcb
from . import config
from . import merge
from . import open_meteo
from . import openaq


FESTIVAL_DATES = [
    "2023-11-12",  # Diwali 2023
    "2024-11-01",  # Diwali 2024
    "2025-10-21",  # Diwali 2025
]


def station_slug(name):
    return name.replace(" ", "_")


def station_file_stems(name):
    slug = station_slug(name)
    return [slug, slug.lower()]


def weather_path(name):
    return Path(config.OUTPUT_DIR) / f"weather_{station_slug(name)}.csv"


def load_or_fetch_weather(station):
    name = station["name"]
    path = weather_path(name)
    if path.exists():
        print(f"  Using cached weather: {path}")
        return pd.read_csv(path)

    weather_df = open_meteo.fetch_historical_weather(
        station["lat"],
        station["lon"],
        config.START_DATE,
        config.END_DATE,
        station_name=name,
    )
    weather_df = open_meteo.add_circular_wind_encoding(weather_df)
    weather_df.to_csv(path, index=False)
    print(f"  -> saved {path} ({len(weather_df)} rows)")
    return weather_df


def load_local_pollutants(name):
    candidates = []
    for stem in station_file_stems(name):
        candidates.extend([
            (Path(config.OUTPUT_DIR) / f"cpcb_{stem}.csv", lambda path: cpcb.load_manual_export(path, station_name=name)),
            (Path(config.OUTPUT_DIR) / f"{stem}_cpcb.csv", lambda path: cpcb.load_manual_export(path, station_name=name)),
            (Path(config.OUTPUT_DIR) / f"openaq_{stem}.csv", pd.read_csv),
        ])

    for path, loader in candidates:
        if path.exists():
            print(f"  Using cached pollutants: {path}")
            return loader(path)
    return pd.DataFrame()


def fetch_openaq_pollutants(station):
    name = station["name"]
    try:
        locations = openaq.find_locations(
            station["lat"],
            station["lon"],
            radius_m=station.get("openaq_radius_m", 5000),
            limit=25,
        )
        location, sensor = openaq.choose_pm25_sensor(
            locations,
            keywords=station.get("openaq_keywords"),
        )
        if sensor is None:
            print("  No nearby OpenAQ PM2.5 sensor found.")
            return pd.DataFrame()

        print(f"  Using OpenAQ {location['name']} PM2.5 sensor {sensor['id']}")
        pollutant_df = openaq.fetch_measurements(
            sensor["id"], config.START_DATE, config.END_DATE, station_name=name
        )
        if pollutant_df.empty:
            return pollutant_df

        path = Path(config.OUTPUT_DIR) / f"openaq_{station_slug(name)}.csv"
        pollutant_df.to_csv(path, index=False)
        print(f"  -> saved {path} ({len(pollutant_df)} rows)")
        return pollutant_df
    except Exception as exc:
        print(f"  OpenAQ unavailable: {exc}")
        print("  Add a CPCB export named data_raw/cpcb_<Station_Name>.csv to continue.")
        return pd.DataFrame()


def build_station_dataset(station):
    name = station["name"]
    print(f"\n=== {name} ===")

    pollutant_df = load_local_pollutants(name)
    if pollutant_df.empty:
        weather_df = load_or_fetch_weather(station)
        pollutant_df = fetch_openaq_pollutants(station)
    elif {"temp", "humidity", "wind_dir_deg"}.issubset(pollutant_df.columns):
        weather_df = pollutant_df[["timestamp", "station"]].copy()
    else:
        weather_df = load_or_fetch_weather(station)

    if pollutant_df.empty:
        print("  Skipped merge/features because pollutant data is missing.")
        return False

    merged = merge.merge_station_data(weather_df, pollutant_df, name)
    merged = merge.regularize_hourly_data(merged)
    merged = merge.drop_all_missing_columns(merged)
    merged = merge.add_festival_flag(merged, FESTIVAL_DATES)
    merged = open_meteo.add_circular_wind_encoding(merged)
    merged = merge.add_pm25_aqi_estimate(merged)

    merged_path = Path(config.OUTPUT_DIR) / f"merged_{station_slug(name)}.csv"
    merged.to_csv(merged_path, index=False)
    print(f"  -> saved {merged_path} ({len(merged)} rows)")

    features = merge.add_lag_features(merged)
    features = merge.add_forecast_targets(features)
    features = merge.add_missingness_features(features)
    features = merge.causally_impute_features(features)
    features_path = Path(config.OUTPUT_DIR) / f"features_{station_slug(name)}.csv"
    features.to_csv(features_path, index=False)
    print(f"  -> saved {features_path} ({len(features)} rows)")
    return True


def run():
    Path(config.OUTPUT_DIR).mkdir(exist_ok=True)
    built = [build_station_dataset(station) for station in config.STATIONS]

    if not any(built):
        print("\nNo training-ready datasets yet. Weather is cached; pollutant data is missing.")
        print("Drop CPCB exports into data_raw, then rerun.")
    else:
        print("\nDone. Use data_raw/features_<station>.csv for model training.")


if __name__ == "__main__":
    run()
