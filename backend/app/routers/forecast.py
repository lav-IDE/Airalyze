import logging

from fastapi import APIRouter, HTTPException
from backend.app.services.forecast_service import get_forecast

router = APIRouter(
    prefix="/forecast",
    tags=["Forecast"]
)
logger = logging.getLogger(__name__)


@router.get("/{ward_id}")
def forecast(ward_id: str):
    normalized_ward_id = ward_id.strip().lower().replace("-", "_").replace(" ", "_")
    try:
        result = get_forecast(normalized_ward_id)
    except LookupError as exc:
        logger.warning("Forecast data unavailable for ward %s: %s", normalized_ward_id, exc)
        raise HTTPException(status_code=404, detail="Forecast data unavailable for this ward") from exc
    except Exception:
        logger.exception("Forecast inference failed for ward %s", normalized_ward_id)
        raise HTTPException(status_code=503, detail="Forecast service temporarily unavailable")

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Ward not found"
        )

    return result
