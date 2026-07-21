"""Stable inference helpers for a future backend or frontend API."""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from .modeling import aqi_band


def load_forecaster(model_path):
    return joblib.load(Path(model_path))


def latest_feature_rows(data_dir, station=None):
    """Load the latest local feature row per station for prototype inference."""
    paths = sorted(Path(data_dir).glob("features_*.csv"))
    if not paths:
        raise FileNotFoundError(f"No features_*.csv files found in {data_dir}")
    data = pd.concat([pd.read_csv(path) for path in paths], ignore_index=True)
    data["timestamp"] = pd.to_datetime(data["timestamp"])
    if station:
        data = data[data["station"].eq(station)]
        if data.empty:
            raise LookupError(f"No data found for station: {station}")
    return data.sort_values("timestamp").groupby("station", as_index=False).tail(1).to_dict(orient="records")


def recent_actuals(data_dir, station, limit=5):
    """Return the latest observed AQI points for a compact dashboard sparkline."""
    paths = sorted(Path(data_dir).glob("features_*.csv"))
    if not paths:
        raise FileNotFoundError(f"No features_*.csv files found in {data_dir}")
    data = pd.concat([pd.read_csv(path) for path in paths], ignore_index=True)
    data["timestamp"] = pd.to_datetime(data["timestamp"])
    rows = data[data["station"].eq(station)].dropna(subset=["aqi"]).sort_values("timestamp").tail(limit)
    if rows.empty:
        raise LookupError(f"No AQI history found for station: {station}")
    return [
        {"timestamp": row.timestamp.isoformat(), "aqi": round(float(row.aqi))}
        for row in rows.itertuples()
    ]


def operational_recommendations(forecast, current_aqi=None):
    """Transparent operational suggestions, not evidence of causal effects."""
    forecast_aqi = forecast["forecast_aqi"]
    trend = "steady" if current_aqi is None else (
        "rising" if forecast_aqi >= current_aqi + 15 else "falling" if forecast_aqi <= current_aqi - 15 else "steady"
    )
    interval = forecast["confidence_interval"]
    uncertainty = "high" if interval["high"] - interval["low"] >= 120 else "moderate"
    actions = ["Verify station readings and notify the city operations desk."]
    if forecast_aqi > 200:
        actions.append("Prioritize roadside dust suppression and construction-compliance checks near the hotspot.")
    if forecast_aqi > 300:
        actions.append("Consider targeted traffic-flow and heavy-vehicle enforcement during the forecast window.")
    if trend == "rising":
        actions.append("Stage field inspection capacity before conditions worsen.")
    if uncertainty == "high":
        actions.append("Confirm with fresh observations before escalating disruptive measures.")
    return {
        "trend": trend,
        "uncertainty": uncertainty,
        "suggested_actions": actions,
        "disclaimer": "Operational suggestions only; forecast associations do not prove intervention effects.",
    }


def prediction_drivers(artifact, limit=5):
    """Return grouped global feature importance for tree-based model artifacts.

    These are model weights, not a claim of causal or per-prediction impact.
    """
    pipeline = artifact.get("model")
    estimator = getattr(pipeline, "named_steps", {}).get("model")
    preprocessor = getattr(pipeline, "named_steps", {}).get("preprocess")
    importances = getattr(estimator, "feature_importances_", None)
    if importances is None or preprocessor is None:
        return []

    names = preprocessor.get_feature_names_out()
    grouped = {}
    for name, importance in zip(names, importances):
        raw_name = name.split("__", 1)[-1]
        label = (
            "Historical AQI" if raw_name.startswith("aqi_lag") else
            "PM2.5 trend" if raw_name.startswith("pm25_lag") or raw_name == "pm25" else
            "Temperature" if raw_name == "temp" else
            "Humidity" if raw_name == "humidity" else
            "Wind conditions" if raw_name.startswith("wind_") else
            "Time and seasonality" if raw_name in {"hour", "day_of_week", "month", "is_festival"} else
            raw_name.replace("_", " ").upper()
        )
        grouped[label] = grouped.get(label, 0) + float(importance)

    total = sum(grouped.values())
    if not total:
        return []
    return [
        {"name": name, "weight": round(weight * 100 / total, 1)}
        for name, weight in sorted(grouped.items(), key=lambda item: item[1], reverse=True)[:limit]
    ]


def predict(artifact, feature_rows):
    """Return JSON-serialisable forecasts for one or more feature rows."""
    rows = pd.DataFrame(feature_rows).copy()
    required = artifact["feature_columns"]
    missing = sorted(set(required) - set(rows.columns))
    if missing:
        raise ValueError(f"Missing inference features: {', '.join(missing)}")

    predictions = np.clip(artifact["model"].predict(rows[required]), 0, 500)
    interval = 1.96 * artifact["residual_rmse"]
    results = []
    for index, prediction in enumerate(predictions):
        row = rows.iloc[index]
        result = {
            "station": row.get("station"),
            "horizon_hours": artifact["horizon_hours"],
            "model": artifact["model_name"],
            "forecast_aqi": round(float(prediction)),
            "aqi_band": aqi_band(prediction),
            "confidence_interval": {
                "low": max(0, round(float(prediction - interval))),
                "high": min(500, round(float(prediction + interval))),
            },
            "prediction_drivers": prediction_drivers(artifact),
        }
        if "timestamp" in rows.columns and pd.notna(row["timestamp"]):
            result["data_timestamp"] = pd.Timestamp(row["timestamp"]).isoformat()
        current_aqi = row.get("aqi") if "aqi" in rows.columns else None
        result["recommendation"] = operational_recommendations(result, current_aqi)
        if "timestamp" in rows.columns and pd.notna(row["timestamp"]):
            forecast_for = pd.Timestamp(row["timestamp"]) + pd.Timedelta(
                hours=artifact["horizon_hours"]
            )
            result["forecast_for"] = forecast_for.isoformat()
        results.append(result)
    return results
