from fastapi import APIRouter
from backend.app.schemas.ward import Ward

router = APIRouter(prefix="/wards", tags=["Wards"])

WARDS = [
    Ward(
        id="anand_vihar",
        name="Anand Vihar",
        lat=28.6469,
        lng=77.3155,
    ),
    Ward(
        id="mandir_marg",
        name="Mandir Marg",
        lat=28.6325,
        lng=77.2067,
    ),
]


@router.get("/", response_model=list[Ward])
def get_wards():
    return WARDS