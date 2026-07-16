# AQI Forecasting — Data Collection Pipeline

Pulls the data described in Decision 5 of the project doc: CPCB (primary),
OpenAQ (automated backup), Open-Meteo (weather).

## What's actually automated

| Source | Automated? | Needs |
|---|---|---|
| Open-Meteo (weather) | ✅ Fully | nothing — no key |
| OpenAQ (PM2.5/AQI, backup) | ✅ Fully | free API key |
| CPCB CCR dashboard (primary) | ❌ Manual export | 5 min per station, see `cpcb.py` |

**Why CPCB isn't a one-command scraper:** see `cpcb.py`'s docstring for
the full reasoning + step-by-step manual export path (short version: no
documented bulk API, session-based Angular dashboard, not worth fighting).

## Setup

```bash
pip install -r requirements.txt
export OPENAQ_API_KEY="your_key_here"   # free: https://explore.openaq.org/register
```

## Run

```bash
python main.py
```

This will, for each station in `config.py`:
1. Pull historical hourly weather from Open-Meteo → `data_raw/weather_<station>.csv`
2. Auto-discover the nearest OpenAQ monitoring location and pull PM2.5 → `data_raw/openaq_<station>.csv`
3. Merge the two into `data_raw/merged_<station>.csv`

If OpenAQ coverage is thin near a station (common — India's OpenAQ density
varies), do the manual CPCB export (`cpcb.py` docstring) and re-run:

```python
import cpcb, merge
cpcb_df = cpcb.load_manual_export("data_raw/cpcb_Anand_Vihar.csv", station_name="Anand Vihar")
weather_df = ...  # already saved from main.py run
merged = merge.merge_station_data(weather_df, cpcb_df, "Anand Vihar")
```

## Before feeding into model training

`merged_<station>.csv` has raw aligned weather + pollutant columns.
You still need to compute, per Decision 7's confirmed feature set:
- `pm25_lag_1h`, `pm25_lag_24h`
- `aqi_lag_1h`, `aqi_lag_24h`, `aqi_lag_168h`

Do this as a separate feature-engineering step (`df.groupby('station')['pm25'].shift(...)`),
**after** this merge — not inside these scrapers — to keep the leakage-avoidance
logic in one auditable place.

## Stations

Currently configured for **Anand Vihar** (traffic corridor, high pollution)
vs. **Lodhi Road** (comparatively green, South Delhi) — see `config.py` for
the reasoning and coordinates. Swap if you find better data quality
elsewhere; Decision 3 says pick by data quality first, contrast second.
