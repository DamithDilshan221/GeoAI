"""Recommendation orchestration service.

Composes NearbySearchService, PedestrianRoutingService, MLInferenceService,
and the domain scoring logic into a single ``get_recommendations`` call.
"""

import logging
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from app.core.config import get_settings
from app.domain.gis.nearby_search_service import NearbySearchService
from app.domain.recommendation.candidate import (
    RecommendationCandidate,
    ScoredCandidate,
)
from app.domain.recommendation.explanation import build_explanation
from app.domain.recommendation.ranking import rank_candidates, score_candidate
from app.domain.recommendation.weights import get_recommendation_weights
from app.domain.routing.pedestrian_routing_service import PedestrianRoutingService
from app.repositories.facility_repository import FacilityRepository
from app.repositories.ml_model_version_repository import MLModelVersionRepository
from app.repositories.recommendation_log_repository import RecommendationLogRepository
from app.services.ml_inference_service import MLInferenceService

logger = logging.getLogger(__name__)

EMPTY_MESSAGE = "No suitable washrooms were found within the current search radius."


@dataclass
class RecommendationResult:
    """Return type for the recommendation pipeline."""

    recommended_facility: ScoredCandidate | None
    ranked_facilities: list[ScoredCandidate]
    explanation: str | None
    message: str | None


class RecommendationService:
    """Orchestrates candidate selection → enrichment → scoring → ranking → logging."""

    def __init__(
        self,
        nearby_search: NearbySearchService,
        routing_service: PedestrianRoutingService,
        ml_service: MLInferenceService,
        facility_repo: FacilityRepository,
        log_repo: RecommendationLogRepository,
        model_version_repo: MLModelVersionRepository,
    ) -> None:
        self._nearby = nearby_search
        self._routing = routing_service
        self._ml = ml_service
        self._facility_repo = facility_repo
        self._log_repo = log_repo
        self._model_version_repo = model_version_repo

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
        4. Best-effort logging to recommendation_logs (one row per scored candidate)
        5. Explanation generation for the top pick
        """
        now = now or datetime.now(UTC)
        settings = get_settings()
        weights = get_recommendation_weights()

        # Step 1 — candidate selection (IS the eligibility filter, decision #1)
        # staff_preferred preference narrows the candidate pool to STAFF facilities;
        # any other preference value (or None) searches across all audiences.
        from app.models.enums import AudienceType  # local import to avoid circular

        audience_filter: AudienceType | None = (
            AudienceType.STAFF if secondary_preference == "staff_preferred" else None
        )

        nearby = self._nearby.find_nearby(
            category_code=category_code,
            audience=audience_filter,
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
            # Full entity for total_stalls/rating/status_updated_at/fixtures
            facility = self._facility_repo.get_by_id(item.id)
            if facility is None:
                continue  # defensive — shouldn't happen

            # Routing — always a fresh OSRM call per §14.2.
            # Returns None only if the facility is inactive/missing (already
            # guarded above), so the fallback branch below is defensive.
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
                # Should not happen (guarded above), but keep defensive path.
                estimated_time_s = item.distance_m / settings.PEDESTRIAN_WALKING_SPEED_MPS
                travel_source = "straight_line_estimate"

            # Usage prediction
            prediction = self._ml.predict_usage(
                facility_id=item.id,
                day_of_week=now.weekday(),
                hour=now.hour,
            )

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

        # Step 4 — best-effort logging (resolved decision #5: never blocks the response).
        # One request_id shared across every row from this call (decision #3).
        # model_version fetched once, reused per candidate — no N+1 (decision #4).
        try:
            request_id = uuid.uuid4()
            model_version = self._model_version_repo.get_active_version()
            for position, scored in enumerate(ranked, start=1):
                cand = scored.candidate
                self._log_repo.log_candidate(
                    request_id=request_id,
                    facility_id=cand.facility.id,
                    category_id=cand.facility.category_id,
                    user_lat=lat,
                    user_lon=lon,
                    radius_m=radius_m,
                    distance_m=cand.distance_m,
                    predicted_usage=cand.predicted_usage,
                    prediction_source=cand.prediction_source,
                    recommendation_score=scored.final_score,
                    rank_position=position,
                    was_top_recommendation=(position == 1),
                    model_version=model_version,
                )
        except Exception:
            logger.warning("Failed to write recommendation_logs rows", exc_info=True)

        # Step 5 — explanation for the top pick
        explanation = build_explanation(ranked[0], weights)

        return RecommendationResult(
            recommended_facility=ranked[0],
            ranked_facilities=ranked,
            explanation=explanation,
            message=None,
        )
