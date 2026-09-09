"""GET /api/v1/recommendations — smart facility recommendation."""

from fastapi import APIRouter, Depends, Query

from app.api.v1.dependencies import get_recommendation_service
from app.domain.ml_inference.crowd_level import derive_crowd_level, resolve_effective_capacity
from app.schemas.recommendation import (
    FacilityRecommendation,
    RecommendationResponse,
)
from app.services.recommendation_service import RecommendationService

router = APIRouter(tags=["recommendations"])


@router.get("/recommendations", response_model=RecommendationResponse)
def get_recommendations(
    lat: float = Query(...),
    lon: float = Query(...),
    category: str = Query(...),
    radius_m: int = Query(default=1000, ge=1, le=10000),
    limit: int = Query(default=25, ge=1, le=50),
    secondary_preference: str | None = Query(default=None),
    service: RecommendationService = Depends(get_recommendation_service),  # noqa: B008
) -> RecommendationResponse:
    """Return ranked facility recommendations based on six scoring factors."""
    result = service.get_recommendations(
        lat=lat,
        lon=lon,
        category_code=category,
        radius_m=radius_m,
        limit=limit,
        secondary_preference=secondary_preference,
    )

    ranked_items: list[FacilityRecommendation] = []
    for position, scored in enumerate(result.ranked_facilities, start=1):
        cand = scored.candidate
        fac = cand.facility

        # Derive the BUCKETED crowd_level for display (distinct from
        # the continuous ratio used internally for scoring).
        eff_cap = resolve_effective_capacity(
            capacity=fac.capacity,
            category_median=None,  # display-only; exact median not critical
        )
        crowd_label = derive_crowd_level(cand.predicted_usage, eff_cap)

        ranked_items.append(
            FacilityRecommendation(
                id=fac.id,
                name=fac.name,
                category=(
                    fac.category_id
                    if isinstance(fac.category_id, str)
                    else str(fac.category_id)
                ),
                status=fac.status.value if hasattr(fac.status, "value") else str(fac.status),
                rating=fac.rating,
                distance_m=round(cand.distance_m, 1),
                estimated_time_s=cand.estimated_time_s,
                travel_source=cand.travel_source,
                predicted_usage=round(cand.predicted_usage, 1),
                crowd_level=crowd_label,
                prediction_source=cand.prediction_source,
                recommendation_score=scored.final_score,
                rank_position=position,
            )
        )

    top = ranked_items[0] if ranked_items else None

    return RecommendationResponse(
        recommended_facility=top,
        ranked_facilities=ranked_items,
        explanation=result.explanation,
        message=result.message,
    )
