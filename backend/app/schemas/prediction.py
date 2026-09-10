from pydantic import BaseModel, Field


class UsagePredictionRequest(BaseModel):
    facility_id: int
    day_of_week: int = Field(ge=0, le=6)
    hour: int = Field(ge=0, le=23)
    recent_usage: float | None = None


class UsagePredictionResponse(BaseModel):
    facility_id: int
    predicted_usage: float
    crowd_level: str
    source: str
    confidence: str
