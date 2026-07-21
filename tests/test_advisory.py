import unittest

from advisory.service import _cache_key, _extract_json_payload, fallback_advisory
from advisory.schemas import ForecastInput, UserProfile
from advisory.service import get_advisory


FORECAST = {
    "station": "Anand Vihar",
    "forecast_aqi": 420,
    "aqi_band": "Severe",
    "horizon_hours": 24,
    "forecast_for": "2026-07-22T09:00:00+05:30",
    "confidence_interval": {"low": 390, "high": 450},
    "model": "test_model",
}


class AdvisoryTests(unittest.TestCase):
    def test_fallback_preserves_the_deterministic_severe_risk(self):
        result = fallback_advisory(FORECAST, {"language": "hi", "health_conditions": ["asthma"]})

        self.assertEqual(result["risk_level"], "severe")
        self.assertEqual(result["display"]["icon"], "stay_indoors")
        self.assertEqual(result["language"], "hi")
        self.assertLessEqual(len(result["display"]["headline_short"].split()), 5)
        self.assertLessEqual(len(result["ivr"]["spoken_text"].split()), 40)

    def test_fallback_supports_punjabi_and_urdu(self):
        pa_res = fallback_advisory(FORECAST, {"language": "pa"})
        self.assertEqual(pa_res["language"], "pa")
        self.assertIn("ਹਵਾ", pa_res["display"]["headline_short"])
        self.assertTrue(any("ਘਰ" in p or "ਮਾਸਕ" in p or "ਬਾਹਰੀ" in p for p in pa_res["app"]["precautions"]))

        ur_res = fallback_advisory(FORECAST, {"language": "ur"})
        self.assertEqual(ur_res["language"], "ur")
        self.assertIn("ہوا", ur_res["app"]["advisory_text"])
        self.assertTrue(any("ماسک" in p or "گریز" in p or "اندر" in p for p in ur_res["app"]["precautions"]))

    def test_cache_key_distinguishes_horizon_and_forecast_time(self):
        profile = UserProfile()
        base = ForecastInput.model_validate(FORECAST)
        later = ForecastInput.model_validate({**FORECAST, "horizon_hours": 1, "forecast_for": "2026-07-22T10:00:00+05:30"})

        self.assertNotEqual(_cache_key(base, profile), _cache_key(later, profile))

    def test_extract_json_payload_handles_code_fences(self):
        payload = _extract_json_payload("```json\n{\"display\": {\"headline_short\": \"Safe\"}}\n```")

        self.assertEqual(payload["display"]["headline_short"], "Safe")

    def test_get_advisory_accepts_forecast_metadata_extras(self):
        forecast = {
            **FORECAST,
            "recent_actuals": [{"timestamp": "2026-07-21T10:00:00", "aqi": 120}],
            "accuracy_metrics": {"model_rmse": 12.0, "baseline_rmse": 18.0, "improvement_percent": 33.3},
            "prediction_drivers": [{"name": "Historical AQI", "weight": 42.0}],
            "recommendation": {"trend": "steady", "uncertainty": "moderate", "suggested_actions": [], "disclaimer": "x"},
        }

        result = get_advisory(forecast, {"language": "en", "health_conditions": ["heart_disease"]})

        self.assertEqual(result["language"], "en")


if __name__ == "__main__":
    unittest.main()
