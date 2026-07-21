import logging
import os
from pathlib import Path

from forecasting.service import (
    load_forecaster,
    latest_feature_rows,
    recent_actuals,
    predict,
)

ROOT = Path(__file__).resolve().parents[3]

logger = logging.getLogger(__name__)
_artifact = None
_artifact_error = None
TRAINING_WINDOW_DAYS = int(os.getenv("AIRALYZE_TRAINING_WINDOW_DAYS", "560"))

# Temporary mapping until frontend and model use the same names
STATION_MAP = {
    "anand_vihar": "Anand Vihar",
    "mandir_marg": "Mandir Marg",
}


def _get_artifact():
    """Load once, but let the route turn a loading failure into JSON 503."""
    global _artifact, _artifact_error
    if _artifact is not None:
        return _artifact
    if _artifact_error is not None:
        raise RuntimeError("Forecast model is unavailable") from _artifact_error

    try:
        _artifact = load_forecaster(ROOT / "artifacts" / "aqi_forecast_1h.joblib")
        return _artifact
    except Exception as exc:
        _artifact_error = exc
        logger.exception("Unable to load forecast model")
        raise RuntimeError("Forecast model is unavailable") from exc


def get_forecast(ward_id: str):
    station = STATION_MAP.get(ward_id)

    if station is None:
        return None

    feature_rows = latest_feature_rows(
        ROOT / "data_raw",
        station=station,
    )

    artifact = _get_artifact()
    result = predict(
        artifact,
        feature_rows,
    )

    forecast = result[0]
    forecast["recent_actuals"] = recent_actuals(ROOT / "data_raw", station=station)
    model_metrics = artifact["metrics"][artifact["model_name"]]["per_station"][station]
    baseline_metrics = artifact["metrics"]["persistence_aqi_lag_1h"]["per_station"][station]
    model_rmse = float(model_metrics["rmse"])
    baseline_rmse = float(baseline_metrics["rmse"])
    forecast["accuracy_metrics"] = {
        "model_rmse": round(model_rmse, 1),
        "baseline_rmse": round(baseline_rmse, 1),
        "improvement_percent": round((baseline_rmse - model_rmse) * 100 / baseline_rmse, 1),
        "training_window_days": TRAINING_WINDOW_DAYS,
    }
    return forecast
