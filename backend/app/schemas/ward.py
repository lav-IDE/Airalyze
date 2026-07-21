from pydantic import BaseModel


class Ward(BaseModel):
    id: str
    name: str
    lat: float
    lng: float