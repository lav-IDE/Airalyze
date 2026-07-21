import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from forecasting.service import latest_feature_rows, load_forecaster, predict


def main():
    parser = argparse.ArgumentParser(description="Print saved AQI forecasts in the CLI.")
    parser.add_argument("--model-path", default="artifacts/aqi_forecast_1h.joblib")
    parser.add_argument("--data-dir", default="data_raw")
    parser.add_argument("--station", help="Optional exact station name")
    args = parser.parse_args()

    artifact = load_forecaster(args.model_path)
    forecasts = predict(artifact, latest_feature_rows(args.data_dir, args.station))
    print(json.dumps(forecasts, indent=2))


if __name__ == "__main__":
    main()
