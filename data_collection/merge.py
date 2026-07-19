"""Merge weather + pollutant sources into one hourly, per-station table."""

import pandas as pd


def regularize_hourly_data(df):
    """Return one row per station and clock hour, preserving source gaps."""
    hourly_frames = []
    for station, station_df in df.groupby("station", sort=False):
        station_df = station_df.sort_values("timestamp").drop_duplicates(
            "timestamp", keep="last"
        )
        hourly_index = pd.date_range(
            station_df["timestamp"].min(),
            station_df["timestamp"].max(),
            freq="h",
            name="timestamp",
        )
        hourly = station_df.set_index("timestamp").reindex(hourly_index)
        hourly["station"] = station
        hourly_frames.append(hourly.reset_index())

    out = pd.concat(hourly_frames, ignore_index=True)
    out["hour"] = out["timestamp"].dt.hour
    out["day_of_week"] = out["timestamp"].dt.dayofweek
    out["month"] = out["timestamp"].dt.month
    return out


def drop_all_missing_columns(df, protected=("timestamp", "station")):
    """Remove unusable fields, such as an entirely empty rainfall column."""
    empty_columns = [
        column
        for column in df.columns
        if column not in protected and df[column].isna().all()
    ]
    return df.drop(columns=empty_columns)


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


def add_forecast_targets(df, horizons=(1, 24)):
    """Add future AQI targets only when the exact forecast hour is present.

    A row at time ``t`` can use observations available at ``t`` as features,
    but its training target must be AQI at a later time.  Checking the future
    timestamp prevents a missing hour from turning a later observation into a
    mislabeled ``t+1`` or ``t+24`` target.
    """
    if "aqi" not in df.columns:
        return df.copy()

    out = df.sort_values(["station", "timestamp"]).copy()
    aqi_by_station_time = (
        out.drop_duplicates(["station", "timestamp"], keep="last")
        .set_index(["station", "timestamp"])["aqi"]
    )
    for hours in horizons:
        future_index = pd.MultiIndex.from_arrays(
            [
                out["station"],
                out["timestamp"] + pd.Timedelta(hours=hours),
            ],
            names=["station", "timestamp"],
        )
        out[f"aqi_target_{hours}h"] = aqi_by_station_time.reindex(
            future_index
        ).to_numpy()

    return out


def add_missingness_features(df):
    """Flag missing model inputs before any causal imputation is applied."""
    out = df.copy()
    excluded = {"timestamp", "station", "aqi", "hour", "day_of_week", "month", "is_festival"}
    feature_columns = [
        column
        for column in out.select_dtypes(include="number").columns
        if column not in excluded and not column.startswith("aqi_target_")
    ]
    for column in feature_columns:
        out[f"{column}_missing"] = out[column].isna().astype(int)
    return out


def causally_impute_features(df, max_gap_hours=24):
    """Forward-fill model inputs from past observations for short outages only."""
    out = df.sort_values(["station", "timestamp"]).copy()
    excluded = {"timestamp", "station", "aqi", "hour", "day_of_week", "month", "is_festival"}
    feature_columns = [
        column
        for column in out.select_dtypes(include="number").columns
        if column not in excluded
        and not column.startswith("aqi_target_")
        and not column.endswith("_missing")
    ]
    out[feature_columns] = out.groupby("station", sort=False)[feature_columns].ffill(
        limit=max_gap_hours
    )
    return out
