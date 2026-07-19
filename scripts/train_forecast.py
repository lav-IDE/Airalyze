import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from forecasting.modeling import save_artifact, train_and_compare


def main():
    parser = argparse.ArgumentParser(description="Train and compare AQI forecast models.")
    parser.add_argument("--data-dir", default="data_raw")
    parser.add_argument("--artifact-dir", default="artifacts")
    parser.add_argument("--horizon-hours", type=int, choices=[1, 24], default=1)
    parser.add_argument("--test-fraction", type=float, default=0.2)
    args = parser.parse_args()

    artifact = train_and_compare(
        data_dir=args.data_dir,
        horizon_hours=args.horizon_hours,
        test_fraction=args.test_fraction,
    )
    model_path, metrics_path = save_artifact(artifact, args.artifact_dir)
    print(f"Selected model: {artifact['model_name']}")
    print(json.dumps(artifact["metrics"], indent=2))
    print(f"Model artifact: {model_path}")
    print(f"Metrics: {metrics_path}")


if __name__ == "__main__":
    main()
