"""Leakage-safe AQI model training, evaluation, and model comparison."""

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesRegressor, HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


TARGET_PREFIX = "aqi_target_"
NON_FEATURE_COLUMNS = {"timestamp", "aqi", "aqi_source"}


def target_column(horizon_hours):
    return f"aqi_target_{horizon_hours}h"


def aqi_band(value):
    """Return the CPCB AQI band for a numeric AQI prediction."""
    if value <= 50:
        return "Good"
    if value <= 100:
        return "Satisfactory"
    if value <= 200:
        return "Moderate"
    if value <= 300:
        return "Poor"
    if value <= 400:
        return "Very Poor"
    return "Severe"


def load_feature_data(data_dir):
    paths = sorted(Path(data_dir).glob("features_*.csv"))
    if not paths:
        raise FileNotFoundError(f"No features_*.csv files found in {data_dir}")

    frames = [pd.read_csv(path, parse_dates=["timestamp"]) for path in paths]
    data = pd.concat(frames, ignore_index=True)
    return data.sort_values(["timestamp", "station"]).reset_index(drop=True)


def select_features(data, target):
    if target not in data.columns:
        raise ValueError(f"Missing training target: {target}")

    training_data = data.dropna(subset=[target]).copy()
    excluded = NON_FEATURE_COLUMNS | {
        column for column in training_data.columns if column.startswith(TARGET_PREFIX)
    }
    feature_columns = [column for column in training_data.columns if column not in excluded]
    numeric_columns = [
        column
        for column in feature_columns
        if column != "station" and pd.api.types.is_numeric_dtype(training_data[column])
    ]
    categorical_columns = ["station"] if "station" in feature_columns else []

    if not numeric_columns:
        raise ValueError("No numeric model features are available")

    return training_data, feature_columns, numeric_columns, categorical_columns


def chronological_split(data, test_fraction=0.2):
    """Reserve the most recent shared period for evaluation."""
    timestamps = np.sort(data["timestamp"].dropna().unique())
    split_index = int(len(timestamps) * (1 - test_fraction))
    if split_index <= 0 or split_index >= len(timestamps):
        raise ValueError("Not enough timestamps for a chronological train/test split")

    cutoff = timestamps[split_index]
    train = data[data["timestamp"] < cutoff].copy()
    test = data[data["timestamp"] >= cutoff].copy()
    if train.empty or test.empty:
        raise ValueError("Chronological split produced an empty partition")
    return train, test, pd.Timestamp(cutoff)


def build_preprocessor(numeric_columns, categorical_columns):
    transformers = [
        ("numeric", SimpleImputer(strategy="median"), numeric_columns),
    ]
    if categorical_columns:
        transformers.append(
            (
                "station",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                categorical_columns,
            )
        )
    return ColumnTransformer(transformers, sparse_threshold=0)


def model_factories():
    return {
        "hist_gradient_boosting": HistGradientBoostingRegressor(
            learning_rate=0.08, max_iter=300, l2_regularization=1.0, random_state=42
        ),
        "random_forest": RandomForestRegressor(
            n_estimators=250, min_samples_leaf=2, n_jobs=-1, random_state=42
        ),
        "extra_trees": ExtraTreesRegressor(
            # Compact deployment candidate.  The previous unconstrained forest
            # used roughly 380 MB per horizon; bounded trees make the artifact
            # practical to load in a thin API while retaining a direct metric
            # comparison during every training run.
            n_estimators=80,
            max_depth=18,
            min_samples_leaf=3,
            max_features=0.8,
            n_jobs=-1,
            random_state=42,
        ),
    }


def evaluate_predictions(actual, predicted):
    actual = np.asarray(actual, dtype=float)
    predicted = np.clip(np.asarray(predicted, dtype=float), 0, 500)
    return {
        "mae": round(float(mean_absolute_error(actual, predicted)), 3),
        "rmse": round(float(root_mean_squared_error(actual, predicted)), 3),
        "r2": round(float(r2_score(actual, predicted)), 3) if len(actual) > 1 else None,
        "aqi_band_accuracy": round(
            float(np.mean([aqi_band(value) == aqi_band(prediction) for value, prediction in zip(actual, predicted)])),
            3,
        ),
    }


def evaluate_by_station(test, target, predicted):
    """Return overall, per-station, and AQI-band error metrics."""
    evaluated = test[["station", target]].copy()
    evaluated["prediction"] = np.clip(np.asarray(predicted, dtype=float), 0, 500)
    metrics = evaluate_predictions(evaluated[target], evaluated["prediction"])
    metrics["per_station"] = {
        station: evaluate_predictions(group[target], group["prediction"])
        for station, group in evaluated.groupby("station", sort=True)
    }
    evaluated["actual_band"] = evaluated[target].map(aqi_band)
    evaluated["predicted_band"] = evaluated["prediction"].map(aqi_band)
    metrics["aqi_category_errors"] = {
        actual_band: {
            predicted_band: int(count)
            for predicted_band, count in group["predicted_band"].value_counts().sort_index().items()
        }
        for actual_band, group in evaluated.groupby("actual_band", sort=False)
    }
    return metrics


def train_and_compare(data_dir="data_raw", horizon_hours=1, test_fraction=0.2):
    target = target_column(horizon_hours)
    data = load_feature_data(data_dir)
    data, feature_columns, numeric_columns, categorical_columns = select_features(data, target)
    train, test, cutoff = chronological_split(data, test_fraction=test_fraction)
    # A training row at t has a label at t + horizon.  Exclude rows whose
    # labels land in the holdout period, not just rows whose features do.
    train = train[train["timestamp"] + pd.Timedelta(hours=horizon_hours) < cutoff].copy()
    if train.empty:
        raise ValueError("No leakage-safe training rows remain before the holdout cutoff")
    x_train, y_train = train[feature_columns], train[target]
    x_test, y_test = test[feature_columns], test[target]

    results = {}
    baseline_mask = test["aqi_lag_1h"].notna()
    if baseline_mask.any():
        results["persistence_aqi_lag_1h"] = evaluate_by_station(
            test.loc[baseline_mask], target, test.loc[baseline_mask, "aqi_lag_1h"]
        )

    fitted_models = {}
    for name, estimator in model_factories().items():
        pipeline = Pipeline(
            [
                ("preprocess", build_preprocessor(numeric_columns, categorical_columns)),
                ("model", estimator),
            ]
        )
        pipeline.fit(x_train, y_train)
        predictions = pipeline.predict(x_test)
        results[name] = evaluate_by_station(test, target, predictions)
        fitted_models[name] = pipeline

    best_name = min(fitted_models, key=lambda name: results[name]["rmse"])
    best_model = fitted_models[best_name]

    # Refit the selected model on all labelled data before saving for backend use.
    best_model.fit(data[feature_columns], data[target])
    artifact = {
        "model": best_model,
        "model_name": best_name,
        "horizon_hours": horizon_hours,
        "target_column": target,
        "feature_columns": feature_columns,
        "metrics": results,
        "test_cutoff": cutoff.isoformat(),
        "residual_rmse": results[best_name]["rmse"],
    }
    return artifact


def save_artifact(artifact, artifact_dir="artifacts"):
    output_dir = Path(artifact_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    horizon = artifact["horizon_hours"]
    model_path = output_dir / f"aqi_forecast_{horizon}h.joblib"
    metrics_path = output_dir / f"aqi_forecast_{horizon}h_metrics.json"
    report_path = output_dir / f"aqi_forecast_{horizon}h_report.md"
    joblib.dump(artifact, model_path, compress=3)
    report = {
        "model_name": artifact["model_name"],
        "horizon_hours": artifact["horizon_hours"],
        "test_cutoff": artifact["test_cutoff"],
        "artifact_size_mb": round(model_path.stat().st_size / 1024**2, 2),
        "metrics": artifact["metrics"],
        "limitations": [
            "AQI target is a PM2.5-derived proxy, not official multi-pollutant CPCB AQI.",
            "Confidence intervals are residual-RMSE heuristics, not calibrated prediction intervals.",
        ],
    }
    metrics_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    rows = ["| Model | RMSE | MAE | AQI-band accuracy |", "|---|---:|---:|---:|"]
    for name, metrics in artifact["metrics"].items():
        rows.append(
            f"| {name} | {metrics['rmse']:.3f} | {metrics['mae']:.3f} | {metrics['aqi_band_accuracy']:.3f} |"
        )
    report_path.write_text(
        "\n".join(
            [
                f"# Airalyze {horizon}-hour model comparison",
                "",
                *rows,
                "",
                f"Selected model: `{artifact['model_name']}`; compressed artifact: `{report['artifact_size_mb']}` MB.",
                "",
                "Target: PM2.5-derived AQI proxy, not official multi-pollutant CPCB AQI.",
            ]
        ),
        encoding="utf-8",
    )
    return model_path, metrics_path
