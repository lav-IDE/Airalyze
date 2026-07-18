"""
Config for the AQI + weather data collection pipeline.

STATIONS picks two real Delhi CAAQMS stations with long, generally clean
historical records and a natural contrast story (per Decision 3):

  - Anand Vihar   : traffic/industrial corridor, consistently among Delhi's
                    worst AQI readings (bus terminal, NH24 traffic).
  - Mandir Marg   : central Delhi station with available CPCB export data.

Swap these if you check the CPCB/OpenAQ data and find gaps — Decision 3
explicitly says pick stations by data quality FIRST, contrast second.
"""

import os
from pathlib import Path


def _load_dotenv(path=".env"):
    dotenv = Path(path)
    if not dotenv.exists():
        return

    for line in dotenv.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


_load_dotenv()


STATIONS = [
    {
        "name": "Anand Vihar",
        "city": "Delhi",
        "lat": 28.6469,
        "lon": 77.3151,
        "openaq_radius_m": 15000,
        "openaq_keywords": ["anand", "vihar", "delhi"],
    },
    {
        "name": "Mandir Marg",
        "city": "Delhi",
        "lat": 28.6364,
        "lon": 77.2012,
        "openaq_radius_m": 25000,
        "openaq_keywords": ["mandir", "marg", "delhi"],
    },
]

# Match the CPCB exports currently available in data_raw.
START_DATE = "2025-01-01"
END_DATE = "2026-07-14"  # keep before "today" for Open-Meteo archive API

# OpenAQ v3 requires a free API key: https://explore.openaq.org/register
# Set it as an env var so it's never hardcoded into this file:
#   export OPENAQ_API_KEY="your_key_here"
OPENAQ_API_KEY_ENV_VAR = "OPENAQ_API_KEY"

OUTPUT_DIR = "data_raw"
