"""Recommendation orchestration service.

Composes NearbySearchService, PedestrianRoutingService, MLInferenceService,
and the domain scoring logic into a single ``get_recommendations`` call.
"""

from dataclasses import dataclass
from datetime import UTC, datetime

from app.core.config import get_settings
from app.domain.gis.nearby_search_service import NearbySearchService
from app.domain.gis.pedestrian_routing_service import PedestrianRoutingService
from app.domain.recommendation.candidate import (
    RecommendationCandidate,
    ScoredCandidate,
)
from app.domain.recommendation.explanation import build_explanation
from app.domain.recommendation.ranking import rank_candidates, score_candidate
from app.domain.recommendation.weights import get_recommendation_weights
from app.repositories.facility_repository import FacilityRepository
from app.services.ml_inference_service import MLInferenceService

EMPTY_MESSAGE = "No suitable facilities were found within the current search radius."


@dataclass
class RecommendationResult:
    """Return type for the recommendation pipeline."""

    recommended_facility: ScoredCandidate | None
    ranked_facilities: list[ScoredCandidate]
    explanation: str | None
    message: str | None


class RecommendationService:
    """Orchestrates candidate selection → enrichment → scoring → ranking."""

    def __init__(
        self,
        nearby_search: NearbySearchService,
        routing_service: PedestrianRoutingService,
        ml_service: MLInferenceService,
        facility_repo: FacilityRepository,
    ) -> None:
        self._nearby = nearby_search
        self._routing = routing_service
        self._ml = ml_service
        self._facility_repo = facility_repo

    def get_recommendations(
        self,
        *,
        lat: float,
        lon: float,
        category_code: str,
        radius_m: int,
        limit: int,
        secondary_preference: str | None = None,
        now: datetime | None = None,
    ) -> RecommendationResult:
        """Full recommendation pipeline.

        1. Candidate selection via NearbySearchService (= eligibility filter)
        2. Enrichment per candidate (full entity, routing, prediction)
        3. Scoring + ranking
        4. Explanation generation for the top pick
        """
        now = now or datetime.now(UTC)
        settings = get_settings()
        weights = get_recommendation_weights()

        # Step 1 — candidate selection (IS the eligibility filter, decision #1)
        nearby = self._nearby.find_nearby(
            category_code=category_code,
            lat=lat,
            lon=lon,
            radius_m=radius_m,
            limit=limit,
        )

        if not nearby:
            return RecommendationResult(
                recommended_facility=None,
                ranked_facilities=[],
                explanation=None,
                message=EMPTY_MESSAGE,
            )

        # Step 2 — enrich and score each candidate
        accessible_only = secondary_preference == "wheelchair_accessible"
        scored_list: list[ScoredCandidate] = []

        for item in nearby:
            # Full entity for capacity/rating/status_updated_at/accessibility
            facility = self._facility_repo.get_by_id(item.id)
            if facility is None:
                continue  # defensive — shouldn't happen

            # Routing
            route = self._routing.get_route(
                origin_lat=lat,
                origin_lon=lon,
                facility_id=item.id,
                accessible_only=accessible_only,
            )

            if route is not None:
                estimated_time_s = float(route.estimated_time_s)
                travel_source = route.source
            else:
                # Routing returned None (facility inactive/missing) — use
                # straight-line from the nearby result's distance
                estimated_time_s = item.distance_m / settings.PEDESTRIAN_WALKING_SPEED_MPS
                travel_source = "straight_line_estimate"

            # Usage prediction
            prediction = self._ml.predict_usage(
                facility_id=item.id,
                day_of_week=now.weekday(),
                hour=now.hour,
            )

            # Category median for crowd scoring
            category_median = self._facility_repo.get_category_median_capacity(facility.category_id)

            candidate = RecommendationCandidate(
                facility=facility,
                distance_m=item.distance_m,
                estimated_time_s=estimated_time_s,
                travel_source=travel_source,  # type: ignore[arg-type]
                predicted_usage=prediction.predicted_usage,
                prediction_source=prediction.source,  # type: ignore[arg-type]
            )

            scored = score_candidate(
                candidate,
                radius_m=float(radius_m),
                now=now,
                secondary_preference=secondary_preference,
                weights=weights,
                walking_speed_mps=settings.PEDESTRIAN_WALKING_SPEED_MPS,
                staleness_horizon_hours=settings.STALENESS_HORIZON_HOURS,
                suitability_penalty=settings.SUITABILITY_PENALTY_SCORE,
                category_median_capacity=category_median,
            )
            scored_list.append(scored)

        if not scored_list:
            return RecommendationResult(
                recommended_facility=None,
                ranked_facilities=[],
                explanation=None,
                message=EMPTY_MESSAGE,
            )

        # Step 3 — rank
        ranked = rank_candidates(scored_list)

        # Step 4 — explanation for the top pick
        explanation = build_explanation(ranked[0], weights)

        return RecommendationResult(
            recommended_facility=ranked[0],
            ranked_facilities=ranked,
            explanation=explanation,
            message=None,
        )
