import unittest
from tempfile import TemporaryDirectory

import pandas as pd

from forecasting.modeling import chronological_split, evaluate_by_station, save_artifact


class ModelingTests(unittest.TestCase):
    def test_holdout_boundary_can_exclude_future_training_labels(self):
        data = pd.DataFrame(
            {
                "station": ["A"] * 10,
                "timestamp": pd.date_range("2026-01-01", periods=10, freq="h"),
                "aqi_target_1h": range(10),
            }
        )
        train, _, cutoff = chronological_split(data, test_fraction=0.2)
        safe_train = train[train["timestamp"] + pd.Timedelta(hours=1) < cutoff]
        self.assertLess(len(safe_train), len(train))
        self.assertTrue((safe_train["timestamp"] + pd.Timedelta(hours=1) < cutoff).all())

    def test_station_and_category_metrics_are_reported(self):
        test = pd.DataFrame(
            {"station": ["A", "A", "B"], "aqi_target_1h": [40, 150, 350]}
        )
        metrics = evaluate_by_station(test, "aqi_target_1h", [45, 220, 290])
        self.assertEqual(set(metrics["per_station"]), {"A", "B"})
        self.assertIn("Good", metrics["aqi_category_errors"])
        self.assertIn("Very Poor", metrics["aqi_category_errors"])

    def test_saved_report_contains_compact_comparison_table(self):
        artifact = {
            "model": {"small": True},
            "model_name": "hist_gradient_boosting",
            "horizon_hours": 1,
            "test_cutoff": "2026-01-01T00:00:00",
            "metrics": {"hist_gradient_boosting": {"rmse": 10.0, "mae": 8.0, "aqi_band_accuracy": 0.8}},
        }
        with TemporaryDirectory() as directory:
            _, metrics_path = save_artifact(artifact, directory)
            report_path = metrics_path.with_name("aqi_forecast_1h_report.md")
            self.assertIn("| hist_gradient_boosting |", report_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
