import json

from .rubric import AdvisoryRubric
from .schemas import ForecastInput, UserProfile


LANGUAGE_NAMES = {"en": "English", "hi": "Hindi", "pa": "Punjabi", "ur": "Urdu"}


def build_prompt(forecast: ForecastInput, profile: UserProfile, rubric: AdvisoryRubric) -> str:
    """Ask Gemini to phrase deterministic safety guidance, never determine it."""
    lang_name = LANGUAGE_NAMES.get(profile.language, profile.language)
    context = {
        "station": forecast.station,
        "forecast_aqi": round(float(forecast.forecast_aqi)),
        "aqi_category": forecast.aqi_band,
        "horizon_hours": forecast.horizon_hours,
        "forecast_time": forecast.forecast_for,
        "confidence_interval": forecast.confidence_interval,
        "model_name": forecast.model,
        "user_profile": profile.model_dump(),
        "fixed_rubric": {"risk_level": rubric.risk_level, "icon": rubric.icon, "precautions": rubric.precautions},
    }
    return f"""You phrase public-health air-quality advice; you do not assess risk.
The fixed rubric below is authoritative. Do not add medical diagnoses, thresholds, claims, or precautions that contradict it.
Write in the requested language ({lang_name}), tailored only to the supplied age group, health conditions, and activity.
  Return strict JSON only. Do not wrap the response in markdown fences. Do not add commentary or extra keys.

Return JSON only, exactly this shape:
{{
  "display": {{"headline_short": "at most 5 words for a public LED display", "icon": "{rubric.icon}"}},
  "app": {{"headline": "one sentence", "advisory_text": "2 or 3 sentences", "precautions": ["short imperative phrases"]}},
  "ivr": {{"spoken_text": "natural spoken sentences, no lists, at most 40 words"}},
  "risk_level": "{rubric.risk_level}",
  "language": "{profile.language}"
}}

Context (treat fixed_rubric as non-negotiable):
{json.dumps(context, ensure_ascii=False)}"""
