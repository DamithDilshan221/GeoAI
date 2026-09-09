"""Aggregate sub-scores into a final weighted score and rank candidates."""

from datetime import datetime

from app.domain.ml_inference.crowd_level import resolve_effective_capacity
from app.domain.recommendation.candidate import (
    RecommendationCandidate,
    ScoredCandidate,
)
from app.domain.recommendation.scoring import (
    crowd_score,
    distance_score,
    freshness_score,
    rating_score,
    suitability_score,
    travel_time_score,
)
from app.domain.recommendation.weights import RecommendationWeights


def score_candidate(
    candidate: RecommendationCandidate,
    *,
    radius_m: float,
    now: datetime,
    secondary_preference: str | None,
    weights: RecommendationWeights,
    walking_speed_mps: float,
    staleness_horizon_hours: float,
    suitability_penalty: float,
    category_median_capacity: float | None,
) -> ScoredCandidate:
    """Compute all six sub-scores and aggregate into a weighted final score."""
    eff_cap = resolve_effective_capacity(
        capacity=candidate.facility.capacity,
        category_median=category_median_capacity,
    )

    sub = {
        "distance": distance_score(candidate.distance_m, radius_m),
        "travel_time": travel_time_score(
            candidate.estimated_time_s, radius_m, walking_speed_mps
        ),
        "freshness": freshness_score(
            candidate.facility.status_updated_at, now, staleness_horizon_hours
        ),
        "crowd": crowd_score(candidate.predicted_usage, eff_cap),
        "rating": rating_score(candidate.facility.rating),
        "suitability": suitability_score(
            candidate.facility.accessibility,
            secondary_preference,
            suitability_penalty,
        ),
    }

    final = (
        weights.distance * sub["distance"]
        + weights.travel_time * sub["travel_time"]
        + weights.crowd * sub["crowd"]
        + weights.rating * sub["rating"]
        + weights.freshness * sub["freshness"]
        + weights.suitability * sub["suitability"]
    )

    return ScoredCandidate(
        candidate=candidate,
        sub_scores=sub,
        final_score=round(final, 2),
    )


def rank_candidates(
    scored: list[ScoredCandidate],
) -> list[ScoredCandidate]:
    """Sort descending by final_score.  Stable sort preserves original
    (distance-ascending) ordering for ties."""
    return sorted(scored, key=lambda s: s.final_score, reverse=True)
