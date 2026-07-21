import logging

from fastapi import APIRouter, HTTPException

from advisory.service import get_advisory
from backend.app.schemas.advisory import AdvisoryRequest, AdvisoryResponse
from backend.app.services.forecast_service import get_forecast

router = APIRouter(
    prefix="/advisory",
    tags=["Advisory"]
)
logger = logging.getLogger(__name__)


@router.post("/{ward_id}", response_model=AdvisoryResponse)
def advisory(ward_id: str, request: AdvisoryRequest):
    normalized_ward_id = ward_id.strip().lower().replace("-", "_").replace(" ", "_")
    try:
        forecast = get_forecast(normalized_ward_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Forecast data unavailable for this ward") from exc
    except Exception as exc:
        logger.exception("Forecast inference failed while creating advisory for %s", normalized_ward_id)
        raise HTTPException(status_code=503, detail="Forecast service temporarily unavailable") from exc
    if forecast is None:
        raise HTTPException(status_code=404, detail="Ward not found")
    return get_advisory(forecast, request.user_profile)
