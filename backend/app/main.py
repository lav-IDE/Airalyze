import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.database import Base, engine
from backend.app.routers import wards, forecast, advisory, auth

app = FastAPI(
    title="Airalyze API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

allowed_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ALLOW_ORIGINS", "").split(",")
    if origin.strip()
]

if allowed_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )


@app.get("/")
def root():
    return {"message": "Backend is running"}


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "Airalyze Backend"
    }


app.include_router(wards.router)
app.include_router(forecast.router)
app.include_router(advisory.router)
app.include_router(auth.router)

from backend.app.database import Base, engine

Base.metadata.create_all(bind=engine)
