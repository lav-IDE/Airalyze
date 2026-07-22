import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from advisory.service import get_advisory
from backend.app.schemas.advisory import AdvisoryRequest, AdvisoryResponse
from backend.app.services.forecast_service import get_forecast
from backend.app.database import get_db
from backend.app.models import PublishedAdvisory

router = APIRouter(
    prefix="/advisory",
    tags=["Advisory"]
)
logger = logging.getLogger(__name__)


class PublishAdvisoryRequest(BaseModel):
    ward_id: str
    language: str
    age_group: str
    health_condition: str
    activity: str
    advisory_text: str


@router.post("/publish")
def publish_advisory(request: PublishAdvisoryRequest, db: Session = Depends(get_db)):
    normalized_ward_id = request.ward_id.strip().lower().replace("-", "_").replace(" ", "_")
    
    # Check if there is an existing published advisory for this ward and profile
    published = db.query(PublishedAdvisory).filter_by(
        ward_id=normalized_ward_id,
        language=request.language,
        age_group=request.age_group,
        health_condition=request.health_condition,
        activity=request.activity
    ).first()
    
    if published:
        published.advisory_text = request.advisory_text
        published.published_at = datetime.utcnow()
    else:
        published = PublishedAdvisory(
            ward_id=normalized_ward_id,
            language=request.language,
            age_group=request.age_group,
            health_condition=request.health_condition,
            activity=request.activity,
            advisory_text=request.advisory_text
        )
        db.add(published)
    
    db.commit()
    return {"status": "success", "message": "Advisory published successfully"}


@router.post("/{ward_id}", response_model=AdvisoryResponse)
def advisory(ward_id: str, request: AdvisoryRequest, db: Session = Depends(get_db)):
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
    
    base_adv = get_advisory(forecast, request.user_profile)
    
    age_group = request.user_profile.age_group
    health_cond = request.user_profile.health_conditions[0] if request.user_profile.health_conditions else "none"
    activity = request.user_profile.activity
    lang = request.user_profile.language
    
    published = db.query(PublishedAdvisory).filter_by(
        ward_id=normalized_ward_id,
        language=lang,
        age_group=age_group,
        health_condition=health_cond,
        activity=activity
    ).first()
    
    if published:
        base_adv["app"]["advisory_text"] = published.advisory_text
        base_adv["is_published"] = True
        
    return base_adv
