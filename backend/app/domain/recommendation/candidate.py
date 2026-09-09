"""Recommendation candidate entities."""

from dataclasses import dataclass
from typing import Literal

from app.domain.entities import Facility


@dataclass(frozen=True)
class RecommendationCandidate:
    """A facility enriched with routing and prediction data, ready for scoring."""

    facility: Facility
    distance_m: float
    estimated_time_s: float
    travel_source: Literal["network", "straight_line_estimate"]
    predicted_usage: float
    prediction_source: Literal["heuristic", "ml_model"]


@dataclass(frozen=True)
class ScoredCandidate:
    """A candidate with computed sub-scores and a weighted final score."""

    candidate: RecommendationCandidate
    sub_scores: dict[str, float]
    final_score: float
