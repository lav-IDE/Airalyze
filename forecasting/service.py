"""Stable inference helpers for a future backend or frontend API."""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from .modeling import aqi_band


def load_forecaster(model_path):
    return joblib.load(Path(model_path))


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
        }
        if "timestamp" in rows.columns and pd.notna(row["timestamp"]):
            forecast_for = pd.Timestamp(row["timestamp"]) + pd.Timedelta(
                hours=artifact["horizon_hours"]
            )
            result["forecast_for"] = forecast_for.isoformat()
        results.append(result)
    return results
