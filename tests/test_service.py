import unittest

import numpy as np

from forecasting.service import operational_recommendations, predict


class FixedModel:
    def predict(self, rows):
        return np.array([325.4] * len(rows))


class ForecastServiceTests(unittest.TestCase):
    def setUp(self):
        self.artifact = {
            "model": FixedModel(),
            "feature_columns": ["station", "pm25"],
            "model_name": "test_model",
            "horizon_hours": 1,
            "residual_rmse": 10.0,
        }

    def test_prediction_is_frontend_ready(self):
        result = predict(
            self.artifact,
            [{"station": "Anand Vihar", "pm25": 220, "timestamp": "2026-07-19 10:00"}],
        )[0]

        self.assertEqual(result["forecast_aqi"], 325)
        self.assertEqual(result["aqi_band"], "Very Poor")
        self.assertEqual(result["confidence_interval"], {"low": 306, "high": 345})
        self.assertEqual(result["forecast_for"], "2026-07-19T11:00:00")
        self.assertEqual(result["data_timestamp"], "2026-07-19T10:00:00")
        self.assertIn("Operational suggestions only", result["recommendation"]["disclaimer"])

    def test_prediction_rejects_missing_features(self):
        with self.assertRaisesRegex(ValueError, "pm25"):
            predict(self.artifact, [{"station": "Anand Vihar"}])

    def test_recommendations_explain_risk_and_uncertainty(self):
        recommendation = operational_recommendations(
            {"forecast_aqi": 330, "confidence_interval": {"low": 200, "high": 460}},
            current_aqi=250,
        )
        self.assertEqual(recommendation["trend"], "rising")
        self.assertEqual(recommendation["uncertainty"], "high")
        self.assertGreaterEqual(len(recommendation["suggested_actions"]), 4)


if __name__ == "__main__":
    unittest.main()
