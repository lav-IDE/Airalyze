from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class MunicipalOfficial(Base):
    __tablename__ = "municipal_officials"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    designation: Mapped[str] = mapped_column(String(120), nullable=False)
    assigned_ward: Mapped[str] = mapped_column(String(80), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class PublishedAdvisory(Base):
    __tablename__ = "published_advisories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ward_id: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    language: Mapped[str] = mapped_column(String(10), nullable=False)
    age_group: Mapped[str] = mapped_column(String(20), nullable=False)
    health_condition: Mapped[str] = mapped_column(String(50), nullable=False)
    activity: Mapped[str] = mapped_column(String(50), nullable=False)
    advisory_text: Mapped[str] = mapped_column(String(1000), nullable=False)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

