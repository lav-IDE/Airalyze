# Airalyze

Airalyze is a Delhi air-quality forecasting prototype built for smart-city intervention use cases. It prepares hourly CPCB station data for Anand Vihar and Mandir Marg, handles missing readings and time gaps, and forecasts estimated AQI one hour and 24 hours ahead.

The project uses CPCB pollutant and weather exports as its primary data source, engineers time, weather, pollutant-lag, and missingness features, then compares multiple machine-learning models against a persistence baseline using a chronological holdout period. The best-performing model is saved as a reusable artifact and can return frontend-ready predictions containing station, forecast AQI, AQI category, forecast time, model name, and an uncertainty interval.

Current AQI values are a PM2.5-based proxy because the available CPCB exports do not include official multi-pollutant CPCB AQI. Airalyze is therefore a forecasting MVP: it demonstrates station-level pollution forecasting and provides a foundation for a future live-data backend, dashboard, hotspot alerts, and intervention recommendations.

## Sources

| Source | Automated? | Used for |
|---|---:|---|
| CPCB manual export | Manual | Primary pollutant + station weather data |
| OpenAQ | Automatic fallback | PM2.5 when local CPCB files are missing |
| Open-Meteo | Automatic fallback | Weather when CPCB weather columns are missing |

CPCB historical exports are not committed to git. Put local exports in `data_raw/`.

## Setup

```bash
pip install -r requirements.txt
copy .env.example .env
```

Then add your OpenAQ key to `.env` if you want the OpenAQ fallback:

```bash
OPENAQ_API_KEY=your_key_here
```

## Expected Local CPCB Files

The current station pair is Anand Vihar and Mandir Marg. The pipeline accepts either naming style:

```text
data_raw/anand_vihar_cpcb.csv
data_raw/mandir_marg_cpcb.csv
```

or:

```text
data_raw/cpcb_Anand_Vihar.csv
data_raw/cpcb_Mandir_Marg.csv
```

The current configured date window is `2025-01-01` to `2026-07-14`.

## Run

```bash
python scripts/collect_data.py
```

For each station, the pipeline:

1. Reuses local CPCB exports when present.
2. Otherwise pulls hourly weather from Open-Meteo and tries OpenAQ PM2.5.
3. Writes `data_raw/merged_<station>.csv`.
4. Writes `data_raw/features_<station>.csv`.

## Training Features

`features_<station>.csv` includes aligned pollutant/weather columns plus:

- `pm25_lag_1h`
- `pm25_lag_24h`
- `aqi_lag_1h`
- `aqi_lag_24h`
- `aqi_lag_168h`
- `aqi_target_1h`
- `aqi_target_24h`

AQI is estimated from PM2.5 when CPCB does not provide an AQI column. It is
therefore a proxy target, not an official CPCB AQI value. Train each forecast
horizon against its explicit future target: for example, use
`aqi_target_1h` for a one-hour forecast. Do not train against the same-row
`aqi`, because it is derived from that row's PM2.5 value. A target is blank
when its exact future timestamp is unavailable, so those rows must be dropped
for that horizon.

## Train Forecast Models

Install the dependencies, build the feature files, then train a horizon:

```bash
python scripts/train_forecast.py --horizon-hours 1
python scripts/train_forecast.py --horizon-hours 24
```

Each run uses a chronological holdout period and compares a persistence
baseline with HistGradientBoosting, RandomForest, and ExtraTrees. The lowest
RMSE ML model is saved under `artifacts/` together with evaluation metrics.
Artifacts are ignored by git.

For a backend, load an artifact and pass one or more feature rows to
`forecasting.service.predict`. It returns JSON-ready station, forecast AQI,
AQI band, horizon, confidence interval, model name, and forecast timestamp.

Print the latest saved forecast for both stations in the terminal:

```bash
python scripts/test_forecast.py
python scripts/test_forecast.py --model-path artifacts/aqi_forecast_24h.joblib
python scripts/test_forecast.py --station "Anand Vihar"
```

## Missing Data

The pipeline restores a complete hourly index per station before building
lags. A missing clock hour is retained as a row with missing observations, so
`*_lag_1h` always means the previous clock hour rather than the previous
available record. Columns with no observations at all are dropped (currently
`rainfall`).

Feature files include `<feature>_missing` flags. Numeric predictor values are
then forward-filled from the same station for at most 24 hours; targets are
never filled. The missing flags retain that information, and values still
missing after 24 hours should be dropped by the training pipeline for the
features it uses.

## GitHub Notes

Ignored on purpose:

- `.env`
- `.venv/`
- `__pycache__/`
- generated/raw files under `data_raw/`
