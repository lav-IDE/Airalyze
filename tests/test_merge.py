import unittest

import pandas as pd

from data_collection.merge import (
    add_forecast_targets,
    add_missingness_features,
    causally_impute_features,
    drop_all_missing_columns,
    regularize_hourly_data,
)


class ForecastTargetsTests(unittest.TestCase):
    def test_targets_use_exact_future_hour_within_each_station(self):
        frame = pd.DataFrame(
            {
                "station": ["A", "A", "A", "B", "B"],
                "timestamp": pd.to_datetime(
                    [
                        "2026-01-01 00:00",
                        "2026-01-01 01:00",
                        "2026-01-01 03:00",  # Missing 02:00.
                        "2026-01-01 00:00",
                        "2026-01-01 01:00",
                    ]
                ),
                "aqi": [100, 120, 140, 200, 220],
            }
        )

        result = add_forecast_targets(frame, horizons=(1,))

        self.assertEqual(result.loc[0, "aqi_target_1h"], 120)
        self.assertTrue(pd.isna(result.loc[1, "aqi_target_1h"]))
        self.assertTrue(pd.isna(result.loc[2, "aqi_target_1h"]))
        self.assertEqual(result.loc[3, "aqi_target_1h"], 220)
        self.assertTrue(pd.isna(result.loc[4, "aqi_target_1h"]))

    def test_target_24h_requires_the_exact_24_hour_timestamp(self):
        frame = pd.DataFrame(
            {
                "station": ["A", "A", "A"],
                "timestamp": pd.to_datetime(
                    ["2026-01-01 00:00", "2026-01-02 00:00", "2026-01-02 01:00"]
                ),
                "aqi": [100, 180, 190],
            }
        )

        result = add_forecast_targets(frame, horizons=(24,))

        self.assertEqual(result.loc[0, "aqi_target_24h"], 180)
        self.assertTrue(pd.isna(result.loc[1, "aqi_target_24h"]))


class MissingDataTests(unittest.TestCase):
    def test_hourly_regularization_prevents_lags_from_crossing_gaps(self):
        frame = pd.DataFrame(
            {
                "station": ["A", "A", "A"],
                "timestamp": pd.to_datetime(
                    ["2026-01-01 00:00", "2026-01-01 01:00", "2026-01-01 03:00"]
                ),
                "pm25": [10, 20, 40],
            }
        )

        regular = regularize_hourly_data(frame)
        with_lags = regular.assign(pm25_lag_1h=regular.groupby("station")["pm25"].shift(1))

        self.assertEqual(len(regular), 4)
        self.assertTrue(pd.isna(with_lags.loc[3, "pm25_lag_1h"]))

    def test_missingness_is_flagged_and_only_short_gaps_are_forward_filled(self):
        frame = pd.DataFrame(
            {
                "station": ["A", "A", "A"],
                "timestamp": pd.date_range("2026-01-01", periods=3, freq="h"),
                "pm25": [10.0, None, None],
                "rainfall": [None, None, None],
                "aqi_target_1h": [100.0, None, 120.0],
            }
        )

        result = causally_impute_features(
            add_missingness_features(drop_all_missing_columns(frame)), max_gap_hours=1
        )

        self.assertNotIn("rainfall", result.columns)
        self.assertEqual(result["pm25_missing"].tolist(), [0, 1, 1])
        self.assertEqual(result.loc[1, "pm25"], 10.0)
        self.assertTrue(pd.isna(result.loc[2, "pm25"]))
        self.assertTrue(pd.isna(result.loc[1, "aqi_target_1h"]))


if __name__ == "__main__":
    unittest.main()
