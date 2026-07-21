import os
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from forecasting.api import create_app


class FixedModel:
    def predict(self, rows):
        return [120.0] * len(rows)


ARTIFACT = {
    "model": FixedModel(),
    "feature_columns": ["station", "pm25"],
    "model_name": "compact_test",
    "horizon_hours": 1,
    "residual_rmse": 8.0,
}
ROWS = [{"station": "Anand Vihar", "pm25": 100, "aqi": 90, "timestamp": "2026-07-19T10:00:00"}]


class ApiTests(unittest.TestCase):
    def test_api_reports_loaded_model_and_latest_forecast(self):
        with patch.dict(os.environ, {"AIRALYZE_HORIZON_HOURS": "1"}), patch(
            "forecasting.api.load_forecaster", return_value=ARTIFACT
        ), patch("forecasting.api.latest_feature_rows", return_value=ROWS):
            with TestClient(create_app()) as client:
                health = client.get("/health")
                latest = client.get("/forecast/latest")

        self.assertEqual(health.json()["active_model"], "compact_test")
        payload = latest.json()
        self.assertEqual(payload["horizon_hours"], 1)
        self.assertEqual(payload["forecasts"][0]["data_timestamp"], "2026-07-19T10:00:00")


if __name__ == "__main__":
    unittest.main()
