"""Small JSON-only FastAPI surface for the Airalyze prototype."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from .service import latest_feature_rows, load_forecaster, predict


def create_app():
    model_path = os.getenv("AIRALYZE_MODEL_PATH", "artifacts/aqi_forecast_1h.joblib")
    data_dir = os.getenv("AIRALYZE_DATA_DIR", "data_raw")
    configured_horizon = int(os.getenv("AIRALYZE_HORIZON_HOURS", "1"))

    @asynccontextmanager
    async def lifespan(app):
        artifact = load_forecaster(model_path)  # exactly one model at startup
        if artifact["horizon_hours"] != configured_horizon:
            raise RuntimeError("AIRALYZE_HORIZON_HOURS does not match the configured model artifact")
        app.state.artifact = artifact
        yield

    app = FastAPI(title="Airalyze API", docs_url=None, redoc_url=None, lifespan=lifespan)

    def response(rows):
        forecasts = predict(app.state.artifact, rows)
        return {
            "active_model": app.state.artifact["model_name"],
            "horizon_hours": app.state.artifact["horizon_hours"],
            "forecasts": forecasts,
        }

    @app.get("/health")
    def health():
        artifact = app.state.artifact
        return {"status": "ok", "active_model": artifact["model_name"], "horizon_hours": artifact["horizon_hours"]}

    @app.get("/forecast/latest")
    def latest():
        try:
            return response(latest_feature_rows(data_dir))
        except FileNotFoundError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    @app.get("/forecast/{station}")
    def station_forecast(station: str):
        try:
            return response(latest_feature_rows(data_dir, station))
        except LookupError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except FileNotFoundError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    return app


app = create_app()
