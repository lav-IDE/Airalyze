from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Language = Literal["en", "hi", "pa", "ur"]
AQICategory = Literal["Good", "Satisfactory", "Moderate", "Poor", "Very Poor", "Severe"]
RiskLevel = Literal["low", "moderate", "high", "severe"]
Icon = Literal["mask_required", "stay_indoors", "safe", "ventilate"]
AgeGroup = Literal["child", "adult", "elderly"]
HealthCondition = Literal["asthma", "none", "heart_disease", "pregnant"]
Activity = Literal["outdoor_worker", "commuter", "indoor", "exercise_planned"]


class UserProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    age_group: AgeGroup = "adult"
    health_conditions: list[HealthCondition] = Field(default_factory=lambda: ["none"])
    activity: Activity = "indoor"
    language: Language = "en"

    @field_validator("health_conditions")
    @classmethod
    def health_conditions_are_consistent(cls, value: list[HealthCondition]) -> list[HealthCondition]:
        if not value or ("none" in value and len(value) > 1):
            raise ValueError("health_conditions must contain 'none' alone or one or more conditions")
        return value


class AdvisoryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_profile: UserProfile = Field(default_factory=UserProfile)


class ForecastInput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    station: str
    forecast_aqi: int | float
    aqi_band: AQICategory
    horizon_hours: int = Field(gt=0)
    forecast_for: str | None = None
    confidence_interval: dict[str, int | float]
    model: str

    @field_validator("confidence_interval")
    @classmethod
    def confidence_interval_has_bounds(cls, value: dict[str, int | float]) -> dict[str, int | float]:
        if "low" not in value or "high" not in value:
            raise ValueError("confidence_interval must contain low and high bounds")
        if float(value["low"]) > float(value["high"]):
            raise ValueError("confidence_interval low must not exceed high")
        return value


class DisplayAdvisory(BaseModel):
    model_config = ConfigDict(extra="forbid")

    headline_short: str
    icon: Icon

    @field_validator("headline_short")
    @classmethod
    def display_headline_is_short(cls, value: str) -> str:
        if len(value.split()) > 5:
            raise ValueError("display headline must have at most five words")
        return value


class AppAdvisory(BaseModel):
    model_config = ConfigDict(extra="forbid")

    headline: str
    advisory_text: str
    precautions: list[str] = Field(min_length=1)


class IVRAdvisory(BaseModel):
    model_config = ConfigDict(extra="forbid")

    spoken_text: str

    @field_validator("spoken_text")
    @classmethod
    def ivr_copy_is_short(cls, value: str) -> str:
        if len(value.split()) > 40:
            raise ValueError("IVR text must have at most 40 words")
        return value


class AdvisoryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    display: DisplayAdvisory
    app: AppAdvisory
    ivr: IVRAdvisory
    risk_level: RiskLevel
    language: Language
