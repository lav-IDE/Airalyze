# Airalyze

Airalyze is a Delhi air-quality forecasting and citizen health-advisory prototype for smart-city intervention use cases. It forecasts estimated AQI for Anand Vihar and Mandir Marg, then turns the forecast into validated, profile-aware guidance for display, app, and IVR channels.

AQI is currently a PM2.5-based proxy because the available CPCB exports do not include official multi-pollutant CPCB AQI. This is a station-level forecasting MVP, not an official AQI or clinical decision system.

## Project Structure

```text
airalyze/
├── advisory/              # Gemini phrasing, CPCB rubric, & validation logic
│   ├── prompt.py
│   ├── rubric.py
│   ├── schemas.py
│   └── service.py
├── backend/               # FastAPI application & REST endpoints
│   └── app/
│       ├── main.py
│       ├── routers/       # Ward, forecast, advisory, & auth routes
│       └── services/      # Forecast integration & service logic
├── data_collection/       # CPCB, OpenAQ, & Open-Meteo ingestion pipelines
├── data_raw/              # Local CPCB data exports & generated feature files
├── forecasting/           # Predictive AQI modeling & inference engine
│   ├── features.py
│   ├── modeling.py
│   └── service.py
├── frontend/              # Vite / React citizen & municipal dashboards
│   └── src/
│       ├── components/    # Reusable UI components & advisory cards
│       ├── pages/         # CitizenDashboard & AdminDashboard
│       └── services/      # Frontend API client
├── scripts/               # Data collection, model training, & verification scripts
└── tests/                 # Unit & integration test suite
```

## Sources

| Source | Automated? | Used for |
|---|---:|---|
| CPCB manual export | Manual | Primary pollutant and station-weather data |
| OpenAQ | Automatic fallback | PM2.5 when local CPCB files are missing |
| Open-Meteo | Automatic fallback | Weather when CPCB weather columns are missing |

CPCB historical exports are not committed to git. Put them in `data_raw/`.

## Setup

```bash
python -m venv .venv
pip install -r requirements.txt
copy .env.example .env
```

Set `GEMINI_API_KEY` to enable LLM phrasing. Without it, the advisory API safely returns deterministic CPCB-rubric guidance. `OPENAQ_API_KEY` is only needed when using the OpenAQ fallback.

## Data and Forecasting

The configured stations are Anand Vihar and Mandir Marg. The pipeline accepts either `data_raw/anand_vihar_cpcb.csv` / `data_raw/mandir_marg_cpcb.csv` or `data_raw/cpcb_Anand_Vihar.csv` / `data_raw/cpcb_Mandir_Marg.csv`.

```bash
python scripts/collect_data.py
python scripts/train_forecast.py --horizon-hours 1
python scripts/train_forecast.py --horizon-hours 24
python scripts/test_forecast.py
```

Feature files contain hourly pollutant/weather data, time features, missingness flags, AQI/PM2.5 lags, and explicit one- and 24-hour future AQI targets. Missing hours are retained so lags keep their clock-hour meaning; inputs are forward-filled for at most 24 hours and targets are never filled.

Training uses a leakage-safe chronological holdout and compares persistence, HistGradientBoosting, RandomForest, and a bounded ExtraTrees model. The selected artifact and metrics report are written under `artifacts/`.

## Advisory Layer

`POST /advisory/{ward_id}` obtains the current ward forecast and accepts a request-scoped citizen profile:

```json
{
  "user_profile": {
    "age_group": "elderly",
    "health_conditions": ["asthma"],
    "activity": "commuter",
    "language": "hi"
  }
}
```

It returns one channel-agnostic JSON response with `display`, `app`, and `ivr` variants. The CPCB AQI category fixes risk level, icon, and base precautions in `advisory/rubric.py`; Gemini only personalizes the wording. Gemini output is Pydantic-validated, cached by station/category/profile/language, and replaced by a static rubric-based fallback on any API or parsing failure.

Run the demo without an API key:

```bash
python scripts/test_advisory.py
```

Use `--live` to call Gemini when `GEMINI_API_KEY` is configured.

## Run the Application

Start the FastAPI backend from the repository root:

```bash
uvicorn backend.app.main:app --reload
```

Start the React dashboard in another terminal:

```bash
cd frontend
npm install
npm run dev
```

The citizen dashboard uses `/wards`, `/forecast/{ward_id}`, and `POST /advisory/{ward_id}`. Municipal authentication is JWT-based and has a separate `/auth` route family.

## Limitations

- Forecast AQI is a PM2.5 proxy, not official multi-pollutant CPCB AQI.
- Confidence intervals are residual-RMSE heuristics, not calibrated prediction intervals.
- Advice is forecast-informed public-health guidance, not medical advice.
- Punjabi and Urdu are supported by the Gemini request schema, and the no-LLM fallback now provides basic copy for all supported languages.
