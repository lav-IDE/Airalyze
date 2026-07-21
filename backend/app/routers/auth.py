import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from dotenv import load_dotenv
env_path = Path(__file__).resolve().parent.parent.parent / ".env"

load_dotenv(env_path)

import jwt
from fastapi import APIRouter, Depends, HTTPException, status,Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models import MunicipalOfficial
from backend.app.schemas.auth import (
    LoginRequest,
    SignupRequest,
    OfficialProfile,
    TokenResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer()
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "240"))

def create_access_token(official: MunicipalOfficial):
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)

    payload = {
        "sub": str(official.id),
        "exp": expires_at,
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token


def current_official(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> MunicipalOfficial:
    try:
        payload = jwt.decode(
            credentials.credentials,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
        )
        official_id = int(payload["sub"])

    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc

    official = db.get(MunicipalOfficial, official_id)

    if official is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Official account not found",
        )

    return official

@router.post("/signup")
def signup(data: SignupRequest, db: Session = Depends(get_db)):
    existing = db.scalar(
        select(MunicipalOfficial).where(
            MunicipalOfficial.email == data.email.lower()
        )
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    official = MunicipalOfficial(
        name=data.name,
        email=data.email.lower(),
        password_hash=password_context.hash(data.password),
        designation=data.designation,
        assigned_ward=data.assigned_ward,
    )

    db.add(official)
    db.commit()
    db.refresh(official)

    return {
        "message": "Official registered successfully"
    }

@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    official = db.scalar(select(MunicipalOfficial).where(MunicipalOfficial.email == credentials.email.lower()))
    if official is None or not password_context.verify(credentials.password, official.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    return TokenResponse(access_token=create_access_token(official))


@router.get("/me", response_model=OfficialProfile)
def me(official: MunicipalOfficial = Depends(current_official)):
    return official
