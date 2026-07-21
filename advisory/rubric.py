"""Deterministic CPCB/NAQI precautions; wording is delegated to the LLM."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AdvisoryRubric:
    risk_level: str
    icon: str
    precautions: tuple[str, ...]


# CPCB National AQI bands. The advisory service must not infer or alter them.
RUBRICS = {
    "Good": AdvisoryRubric("low", "safe", ("Enjoy normal outdoor activity.",)),
    "Satisfactory": AdvisoryRubric("low", "ventilate", ("Sensitive people should watch for discomfort.",)),
    "Moderate": AdvisoryRubric("moderate", "ventilate", ("Reduce prolonged outdoor exertion if you have breathing discomfort.",)),
    "Poor": AdvisoryRubric("high", "mask_required", ("Limit prolonged outdoor exertion.", "Wear a well-fitted mask outdoors if sensitive to pollution.")),
    "Very Poor": AdvisoryRubric("high", "stay_indoors", ("Avoid prolonged outdoor activity.", "Keep children, older adults, and people with heart or lung conditions indoors where possible.", "Use a well-fitted mask if travel is necessary.")),
    "Severe": AdvisoryRubric("severe", "stay_indoors", ("Stay indoors where possible.", "Avoid outdoor exercise and strenuous work.", "Use a well-fitted mask if going outside is unavoidable.")),
}


def rubric_for(aqi_category: str) -> AdvisoryRubric:
    try:
        return RUBRICS[aqi_category]
    except KeyError as exc:
        raise ValueError(f"Unsupported CPCB AQI category: {aqi_category}") from exc
