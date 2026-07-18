# AQI Forecasting Data Pipeline

Data collection and feature-building pipeline for a Delhi AQI forecasting prototype.

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

AQI is estimated from PM2.5 when CPCB does not provide an AQI column.

## GitHub Notes

Ignored on purpose:

- `.env`
- `.venv/`
- `__pycache__/`
- generated/raw files under `data_raw/`
