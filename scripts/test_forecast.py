import argparse
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from forecasting.service import load_forecaster, predict


def latest_feature_rows(data_dir, station=None):
    paths = sorted(Path(data_dir).glob("features_*.csv"))
    if not paths:
        raise FileNotFoundError(f"No features_*.csv files found in {data_dir}")

    data = pd.concat([pd.read_csv(path) for path in paths], ignore_index=True)
    data["timestamp"] = pd.to_datetime(data["timestamp"])
    if station:
        data = data[data["station"].eq(station)]
        if data.empty:
            raise ValueError(f"No data found for station: {station}")

    return (
        data.sort_values("timestamp")
        .groupby("station", as_index=False)
        .tail(1)
        .to_dict(orient="records")
    )


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
