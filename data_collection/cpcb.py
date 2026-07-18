import pandas as pd


def load_manual_export(csv_path, station_name=""):
    """Normalize a manually-downloaded CPCB CSV into pipeline schema.
    CPCB exports commonly use a 'From Date'/'To Date' or single
    'Timestamp' column and per-pollutant columns (PM2.5, PM10, NO2, ...).
    Adjust the rename map below to match whatever your actual export
    file's headers look like — CPCB has changed export formats before.
    """
    df = pd.read_csv(csv_path)

    rename_map = {
        "From Date": "timestamp",
        "Timestamp": "timestamp",
        "PM2.5": "pm25",
        "PM2.5 (ug/m3)": "pm25",
        "PM10": "pm10",
        "NO": "no",
        "NO2": "no2",
        "NOX": "nox",
        "NH3": "nh3",
        "SO2": "so2",
        "CO": "co",
        "OZONE": "ozone",
        "AT": "temp",
        "RH": "humidity",
        "WS": "wind_speed",
        "WD": "wind_dir_deg",
        "BP": "pressure",
        "RF": "rainfall",
        "AQI": "aqi",
    }
    df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns},
              inplace=True)

    if "timestamp" not in df.columns:
        raise ValueError(
            f"Couldn't find a timestamp column in {csv_path}. "
            f"Columns found: {list(df.columns)} — update rename_map."
        )

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", dayfirst=True)
    df["station"] = station_name
    keep_cols = [
        c for c in [
            "timestamp",
            "station",
            "pm25",
            "pm10",
            "no",
            "no2",
            "nox",
            "nh3",
            "so2",
            "co",
            "ozone",
            "temp",
            "humidity",
            "wind_speed",
            "wind_dir_deg",
            "pressure",
            "rainfall",
            "aqi",
        ]
        if c in df.columns
    ]
    return df[keep_cols].dropna(subset=["timestamp"])
