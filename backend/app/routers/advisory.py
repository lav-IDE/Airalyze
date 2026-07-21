from fastapi import APIRouter, HTTPException
from backend.app.services.advisory_service import generate_advisory

router = APIRouter(
    prefix="/advisory",
    tags=["Advisory"]
)


@router.get("/{ward_id}")
def advisory(ward_id: str):
    result = generate_advisory(ward_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Ward not found"
        )

    return result