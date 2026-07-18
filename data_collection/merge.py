"""Merge weather + pollutant sources into one hourly, per-station table."""

import pandas as pd


def merge_station_data(weather_df, pollutant_df, station_name):
    """weather_df: from open_meteo.fetch_historical_weather()
       pollutant_df: from openaq.fetch_measurements() or cpcb.load_manual_export()
       Both need a 'timestamp' column; merges on the hour.
    """
    w = weather_df.copy()
    p = pollutant_df.copy()

    is_openaq_shape = "value" in p.columns
    w["timestamp"] = pd.to_datetime(w["timestamp"]).dt.tz_localize(None)
    if is_openaq_shape:
        p["timestamp"] = (
            pd.to_datetime(p["timestamp"], utc=True)
            .dt.tz_convert("Asia/Kolkata")
            .dt.tz_localize(None)
        )
    else:
        p["timestamp"] = pd.to_datetime(p["timestamp"]).dt.tz_localize(None)
    w["timestamp"] = w["timestamp"].dt.floor("h")
    p["timestamp"] = p["timestamp"].dt.floor("h")
    p = p.drop(columns=["station"], errors="ignore")

    if is_openaq_shape and "parameter" in p.columns:  # OpenAQ multi-parameter shape
        p = p.pivot_table(index="timestamp", columns="parameter",
                           values="value", aggfunc="mean").reset_index()
    elif is_openaq_shape:  # OpenAQ single pm25 sensor shape
        p = p.rename(columns={"value": "pm25"})

    merged = pd.merge(w, p, on="timestamp", how="outer", suffixes=("", "_pollutant"))
    merged["station"] = station_name
    merged.sort_values("timestamp", inplace=True)

    merged["hour"] = merged["timestamp"].dt.hour
    merged["day_of_week"] = merged["timestamp"].dt.dayofweek
    merged["month"] = merged["timestamp"].dt.month

    return merged


def add_festival_flag(df, festival_dates):
    """festival_dates: list of 'YYYY-MM-DD' strings (Diwali etc.) —
    keep this as the hardcoded lookup table from Decision 5."""
    dates = pd.to_datetime(festival_dates).normalize()
    df["is_festival"] = df["timestamp"].dt.normalize().isin(dates).astype(int)
    return df


def add_pm25_aqi_estimate(df):
    """Estimate AQI from PM2.5 if source AQI is absent."""
    if "aqi" in df.columns or "pm25" not in df.columns:
        return df

    # ponytail: hourly PM2.5 AQI is a demo proxy; upgrade to CPCB 24h sub-index
    # calculation when official pollutant history is available.
    breakpoints = [
        (0, 30, 0, 50),
        (31, 60, 51, 100),
        (61, 90, 101, 200),
        (91, 120, 201, 300),
        (121, 250, 301, 400),
        (251, 350, 401, 500),
    ]

    def estimate(pm25):
        if pd.isna(pm25):
            return pd.NA
        for c_low, c_high, i_low, i_high in breakpoints:
            if c_low <= pm25 <= c_high:
                return round(((i_high - i_low) / (c_high - c_low)) * (pm25 - c_low) + i_low)
        return 500

    df["aqi"] = df["pm25"].apply(estimate)
    df["aqi_source"] = "estimated_from_pm25"
    return df


def add_lag_features(df):
    """Add leakage-safe lag features after weather/pollutants are aligned."""
    out = df.sort_values(["station", "timestamp"]).copy()
    for col, hours in [("pm25", 1), ("pm25", 24), ("aqi", 1), ("aqi", 24), ("aqi", 168)]:
        if col in out.columns:
            out[f"{col}_lag_{hours}h"] = out.groupby("station")[col].shift(hours)
    return out
