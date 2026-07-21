"""Print deterministic advisory examples; pass --live to use Gemini when configured."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.stdout.reconfigure(encoding="utf-8")
from advisory.service import fallback_advisory, get_advisory


def forecast(station, aqi, band):
    return {
        "station": station, "forecast_aqi": aqi, "aqi_band": band, "horizon_hours": 24,
        "forecast_for": "2026-07-22T09:00:00+05:30", "confidence_interval": {"low": aqi - 20, "high": aqi + 20},
        "model": "demo_forecaster",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="Use Gemini instead of deterministic fallback")
    args = parser.parse_args()
    profile = {"age_group": "elderly", "health_conditions": ["asthma"], "activity": "commuter", "language": "hi"}
    for station, aqi, band in [("Anand Vihar", 420, "Severe"), ("Mandir Marg", 180, "Moderate")]:
        data = forecast(station, aqi, band)
        advisory = get_advisory(data, profile) if args.live else fallback_advisory(data, profile)
        print(json.dumps(advisory, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
