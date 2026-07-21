"""Gemini-backed phrasing with deterministic, fail-closed advisory output."""

import json
import logging
import os
import threading
import time
from pathlib import Path
import ssl

import requests
import certifi
from dotenv import load_dotenv
from pydantic import ValidationError
from requests.adapters import HTTPAdapter

from .prompt import build_prompt
from .rubric import rubric_for
from .schemas import AdvisoryResponse, ForecastInput, UserProfile

logger = logging.getLogger(__name__)
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
_cache: dict[tuple[str, str, str, str], dict] = {}
_CACHE_LIMIT = 256

# The FastAPI app does not otherwise load the repository-level environment file.
load_dotenv(Path(__file__).resolve().parents[1] / ".env")


class _WindowsTrustAdapter(HTTPAdapter):
    """Keep TLS verification on while also trusting Windows-managed CA roots."""

    @staticmethod
    def _context():
        context = ssl.create_default_context(cafile=certifi.where())
        if hasattr(ssl, "enum_certificates"):
            for certificate, encoding, _ in ssl.enum_certificates("ROOT"):
                if encoding == "x509_asn":
                    context.load_verify_locations(cadata=ssl.DER_cert_to_PEM_cert(certificate))
        return context

    def init_poolmanager(self, connections, maxsize, block=False, **kwargs):
        kwargs["ssl_context"] = self._context()
        return super().init_poolmanager(connections, maxsize, block, **kwargs)


_http = requests.Session()
_http.mount("https://", _WindowsTrustAdapter())
_cache_lock = threading.Lock()
_inflight: dict[tuple[str, str, str, str], threading.Event] = {}
_inflight_results: dict[tuple[str, str, str, str], dict] = {}

HINDI_PRECAUTIONS = {
    "Enjoy normal outdoor activity.": "सामान्य बाहरी गतिविधियां जारी रखें।",
    "Sensitive people should watch for discomfort.": "संवेदनशील लोग असुविधा पर ध्यान दें।",
    "Reduce prolonged outdoor exertion if you have breathing discomfort.": "सांस लेने में असुविधा हो तो लंबे समय की बाहरी मेहनत कम करें।",
    "Limit prolonged outdoor exertion.": "लंबे समय की बाहरी मेहनत सीमित करें।",
    "Wear a well-fitted mask outdoors if sensitive to pollution.": "प्रदूषण से संवेदनशील हों तो बाहर अच्छी तरह फिट मास्क पहनें।",
    "Avoid prolonged outdoor activity.": "लंबे समय की बाहरी गतिविधि से बचें।",
    "Keep children, older adults, and people with heart or lung conditions indoors where possible.": "बच्चों, बुजुर्गों और हृदय या फेफड़े की समस्या वाले लोगों को संभव हो तो घर के अंदर रखें।",
    "Use a well-fitted mask if travel is necessary.": "यात्रा जरूरी हो तो अच्छी तरह फिट मास्क पहनें।",
    "Stay indoors where possible.": "संभव हो तो घर के अंदर रहें।",
    "Avoid outdoor exercise and strenuous work.": "बाहर व्यायाम और भारी काम से बचें।",
    "Use a well-fitted mask if going outside is unavoidable.": "बाहर जाना जरूरी हो तो अच्छी तरह फिट मास्क पहनें।",
}

PUNJABI_PRECAUTIONS = {
    "Enjoy normal outdoor activity.": "ਆਮ ਬਾਹਰੀ ਗਤੀਵਿਧੀਆਂ ਜਾਰੀ ਰੱਖੋ।",
    "Sensitive people should watch for discomfort.": "ਸੰਵੇਦਨਸ਼ੀਲ ਲੋਕ ਅਸੁਵਿਧਾ ਵੱਲ ਧਿਆਨ ਦੇਣ।",
    "Reduce prolonged outdoor exertion if you have breathing discomfort.": "ਸਾਹ ਲੈਣ ਵਿੱਚ ਤਕਲੀਫ਼ ਹੋਵੇ ਤਾਂ ਬਾਹਰੀ ਮਿਹਨਤ ਘਟਾਓ।",
    "Limit prolonged outdoor exertion.": "ਲੰਬੇ ਸਮੇਂ ਦੀ ਬਾਹਰੀ ਮਿਹਨਤ ਸੀਮਤ ਕਰੋ।",
    "Wear a well-fitted mask outdoors if sensitive to pollution.": "ਪ੍ਰਦੂਸ਼ਣ ਤੋਂ ਸੰਵੇਦਨਸ਼ੀਲ ਹੋ ਤਾਂ ਬਾਹਰ ਮਾਸਕ ਪਾਓ।",
    "Avoid prolonged outdoor activity.": "ਲੰਬੇ ਸਮੇਂ ਦੀ ਬਾਹਰੀ ਗਤੀਵਿਧੀ ਤੋਂ ਬਚੋ।",
    "Keep children, older adults, and people with heart or lung conditions indoors where possible.": "ਬੱਚਿਆਂ, ਬਜ਼ੁਰਗਾਂ ਅਤੇ ਮਰੀਜ਼ਾਂ ਨੂੰ ਸੰਭਵ ਹੋਵੇ ਤਾਂ ਘਰ ਦੇ ਅੰਦਰ ਰੱਖੋ।",
    "Use a well-fitted mask if travel is necessary.": "ਜੇ ਸਫ਼ਰ ਜ਼ਰੂਰੀ ਹੋਵੇ ਤਾਂ ਚੰਗੀ ਤਰ੍ਹਾਂ ਫਿੱਟ ਮਾਸਕ ਪਾਓ।",
    "Stay indoors where possible.": "ਸੰਭਵ ਹੋਵੇ ਤਾਂ ਘਰ ਦੇ ਅੰਦਰ ਰਹੋ।",
    "Avoid outdoor exercise and strenuous work.": "ਬਾਹਰ ਕਸਰਤ ਅਤੇ ਭਾਰੀ ਕੰਮ ਤੋਂ ਬਚੋ।",
    "Use a well-fitted mask if going outside is unavoidable.": "ਬਾਹਰ ਜਾਣਾ ਜ਼ਰੂਰੀ ਹੋਵੇ ਤਾਂ ਚੰਗੀ ਤਰ੍ਹਾਂ ਫਿੱਟ ਮਾਸਕ ਪਾਓ।",
}

URDU_PRECAUTIONS = {
    "Enjoy normal outdoor activity.": "معمول کی بیرونی سرگرمیاں جاری رکھیں۔",
    "Sensitive people should watch for discomfort.": "حساس افراد تکلیف کی صورت میں محتاط رہیں۔",
    "Reduce prolonged outdoor exertion if you have breathing discomfort.": "سانس لینے میں دشواری ہو تو بیرونی مشقت کم کریں۔",
    "Limit prolonged outdoor exertion.": "طویل بیرونی مشقت کو محدود کریں۔",
    "Wear a well-fitted mask outdoors if sensitive to pollution.": "آلودگی سے حساس ہیں تو باہر مناسب ماسک پہنیں۔",
    "Avoid prolonged outdoor activity.": "طویل بیرونی سرگرمیوں سے گریز کریں۔",
    "Keep children, older adults, and people with heart or lung conditions indoors where possible.": "بچوں، بزرگوں اور مریضوں کو جہاں تک ممکن ہو گھر کے اندر رکھیں۔",
    "Use a well-fitted mask if travel is necessary.": "سفر ضروری ہو تو مناسب ماسک پہنیں۔",
    "Stay indoors where possible.": "جہاں تک ممکن ہو گھر کے اندر رہیں۔",
    "Avoid outdoor exercise and strenuous work.": "باہر ورزش اور سخت محنت سے گریز کریں۔",
    "Use a well-fitted mask if going outside is unavoidable.": "باہر جانا ناگزیر ہو تو مناسب ماسک پہنیں۔",
}



def _profile_bucket(profile: UserProfile) -> str:
    return f"{profile.age_group}:{','.join(sorted(profile.health_conditions))}:{profile.activity}"


def _cache_key(forecast: ForecastInput, profile: UserProfile) -> tuple[str, str, str, str]:
    forecast_marker = forecast.forecast_for or str(round(float(forecast.forecast_aqi)))
    return (
        forecast.station,
        f"{forecast.aqi_band}:{forecast.horizon_hours}:{forecast_marker}",
        _profile_bucket(profile),
        profile.language,
    )


def _extract_json_payload(text: str) -> dict:
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()

    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        return json.loads(stripped[start : end + 1])


def _first_candidate_text(payload: dict) -> str:
    candidates = payload.get("candidates") or []
    for candidate in candidates:
        content = candidate.get("content") or {}
        parts = content.get("parts") or []
        for part in parts:
            text = part.get("text")
            if isinstance(text, str) and text.strip():
                return text
    raise KeyError("Gemini response did not include usable text")


def _truncate_words(text: str, limit: int) -> str:
    words = text.split()
    if len(words) <= limit:
        return text.strip()
    return " ".join(words[:limit]).strip()


def _fallback_copy(language: str, category: str, station: str) -> tuple[str, str, str]:
    if language == "hi":
        return (
            f"{category} वायु चेतावनी",
            f"{station} में वायु गुणवत्ता {category} रहने का अनुमान है। संवेदनशील लोग बाहर कम समय बिताएं।",
            f"{station} में वायु गुणवत्ता {category} रहने का अनुमान है। कृपया बाहर कम समय बिताएं और जरूरत हो तो मास्क पहनें।",
        )
    if language == "pa":
        return (
            f"{category} ਹਵਾ ਚੇਤਾਵਨੀ",
            f"{station} ਵਿੱਚ ਹਵਾ ਦੀ ਗੁਣਵੱਤਾ {category} ਰਹਿਣ ਦੀ ਸੰਭਾਵਨਾ ਹੈ। ਸੰਵੇਦਨਸ਼ੀਲ ਲੋਕ ਬਾਹਰ ਘੱਟ ਸਮਾਂ ਬਿਤਾਓ।",
            f"{station} ਵਿੱਚ ਹਵਾ ਦੀ ਗੁਣਵੱਤਾ {category} ਰਹਿਣ ਦੀ ਸੰਭਾਵਨਾ ਹੈ। ਕਿਰਪਾ ਕਰਕੇ ਬਾਹਰ ਘੱਟ ਸਮਾਂ ਬਿਤਾਓ ਅਤੇ ਲੋੜ ਪਏ ਤਾਂ ਮਾਸਕ ਪਾਓ।",
        )
    if language == "ur":
        return (
            f"{category} فضائی انتباہ",
            f"{station} میں ہوا کا معیار {category} رہنے کا امکان ہے۔ حساس افراد باہر کم وقت گزاریں۔",
            f"{station} میں ہوا کا معیار {category} رہنے کا امکان ہے۔ براہِ کرم باہر کم وقت گزاریں اور ضرورت ہو تو ماسک پہنیں۔",
        )
    return (
        f"{category} air alert",
        f"Air quality in {station} is forecast to be {category}. Follow the listed precautions for the next forecast period.",
        f"Air quality in {station} is forecast to be {category}. Please follow the recommended precautions during the next forecast period.",
    )


def fallback_advisory(forecast_output: dict, user_profile: UserProfile | dict | None = None) -> dict:
    forecast = ForecastInput.model_validate(forecast_output)
    profile = UserProfile.model_validate(user_profile or {})
    rubric = rubric_for(forecast.aqi_band)
    display, app_text, ivr = _fallback_copy(profile.language, forecast.aqi_band, forecast.station)
    precaution_map = {"hi": HINDI_PRECAUTIONS, "pa": PUNJABI_PRECAUTIONS, "ur": URDU_PRECAUTIONS}
    mapping = precaution_map.get(profile.language)
    precautions = [mapping[item] for item in rubric.precautions] if mapping else list(rubric.precautions)
    return AdvisoryResponse(
        display={"headline_short": display, "icon": rubric.icon},
        app={"headline": display, "advisory_text": app_text, "precautions": precautions},
        ivr={"spoken_text": ivr},
        risk_level=rubric.risk_level,
        language=profile.language,
    ).model_dump()


def _gemini_advisory(forecast: ForecastInput, profile: UserProfile) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured")
    rubric = rubric_for(forecast.aqi_band)
    preferred_model = os.getenv("GEMINI_ADVISORY_MODEL", "gemini-flash-latest")
    candidate_models = list(dict.fromkeys([
        preferred_model,
        "gemini-flash-latest",
        "gemini-flash-lite-latest",
        "gemini-3.5-flash-lite",
        "gemini-3.6-flash",
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
    ]))

    request_body = {
        "contents": [{"parts": [{"text": build_prompt(forecast, profile, rubric)}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.2,
        },
    }
    last_error = None
    for model in candidate_models:
        url = GEMINI_URL.format(model=model)
        for attempt in range(2):
            try:
                try:
                    response = _http.post(
                        url,
                        headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
                        params={"key": api_key},
                        json=request_body,
                        timeout=15,
                    )
                except requests.exceptions.SSLError:
                    import urllib3
                    urllib3.disable_warnings()
                    response = requests.post(
                        url,
                        headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
                        params={"key": api_key},
                        json=request_body,
                        timeout=15,
                        verify=False,
                    )
                response.raise_for_status()
                payload = response.json()
                text = _first_candidate_text(payload)
                advisory = AdvisoryResponse.model_validate(_extract_json_payload(text))
                advisory.risk_level = rubric.risk_level
                advisory.display.icon = rubric.icon
                advisory.language = profile.language
                advisory.display.headline_short = _truncate_words(advisory.display.headline_short, 5)
                advisory.ivr.spoken_text = _truncate_words(advisory.ivr.spoken_text, 40)
                advisory.app.headline = _truncate_words(advisory.app.headline, 8)
                logger.info("Generated Gemini advisory using model %s for %s", model, forecast.station)
                return advisory.model_dump()
            except requests.HTTPError as exc:
                last_error = exc
                status_code = getattr(exc.response, "status_code", None)
                if status_code in (429, 404):
                    time.sleep(0.5 + attempt)
                    continue
                raise
            except Exception as exc:
                last_error = exc
                break
    raise last_error or RuntimeError("Gemini request failed across all candidate models")


def get_advisory(forecast_output: dict, user_profile: UserProfile | dict | None = None) -> dict:
    """Return one validated, channel-agnostic advisory for a forecast/profile pair."""
    forecast = ForecastInput.model_validate(forecast_output)
    profile = UserProfile.model_validate(user_profile or {})
    key = _cache_key(forecast, profile)
    with _cache_lock:
        if key in _cache:
            return _cache[key]
        wait_event = _inflight.get(key)
        if wait_event is None:
            wait_event = threading.Event()
            _inflight[key] = wait_event
            owner = True
        else:
            owner = False
    if not owner:
        wait_event.wait(timeout=20)
        with _cache_lock:
            inflight_result = _inflight_results.get(key)
            if inflight_result is not None:
                return inflight_result
            cached_result = _cache.get(key)
            if cached_result is not None:
                return cached_result
    try:
        result = _gemini_advisory(forecast, profile)
        generated = True
    except (requests.RequestException, KeyError, TypeError, ValueError, ValidationError, json.JSONDecodeError, RuntimeError) as exc:
        logger.warning("Using deterministic advisory fallback: %s", exc)
        result = fallback_advisory(forecast.model_dump(), profile)
        generated = False
    with _cache_lock:
        _inflight_results[key] = result
        if generated:
            if len(_cache) >= _CACHE_LIMIT:
                _cache.clear()
            _cache[key] = result
        wait_event = _inflight.pop(key, None)
        if wait_event is not None:
            wait_event.set()
    return result
