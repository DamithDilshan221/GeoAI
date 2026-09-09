"""Response schemas for the recommendation endpoint."""

from pydantic import BaseModel


class FacilityRecommendation(BaseModel):
    """A single scored facility in the recommendation response."""

    id: int
    name: str
    category: str
    status: str
    rating: float | None
    distance_m: float
    estimated_time_s: float
    travel_source: str
    predicted_usage: float
    crowd_level: str
    prediction_source: str
    recommendation_score: float
    rank_position: int


class RecommendationResponse(BaseModel):
    """Top-level response for GET /api/v1/recommendations."""

    recommended_facility: FacilityRecommendation | None
    ranked_facilities: list[FacilityRecommendation]
    explanation: str | None
    message: str | None
