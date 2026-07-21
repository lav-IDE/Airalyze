import unittest

from backend.app.services.forecast_service import _station_metrics


class ForecastMetricCompatibilityTests(unittest.TestCase):
    def test_old_artifacts_without_per_station_metrics_use_overall_metrics(self):
        artifact = {"metrics": {"model": {"rmse": 61.9}}}

        self.assertEqual(_station_metrics(artifact, "model", "Anand Vihar"), {"rmse": 61.9})


if __name__ == "__main__":
    unittest.main()
