"""Recommendation weights — loaded once from YAML, cached for the process lifetime."""

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import yaml

from app.core.config import get_settings


@dataclass(frozen=True)
class RecommendationWeights:
    """Six factor weights that must sum to 1.0 (±0.001)."""

    distance: float
    travel_time: float
    crowd: float
    rating: float
    freshness: float
    suitability: float


@lru_cache
def get_recommendation_weights() -> RecommendationWeights:
    """Load weights from the YAML config path and validate their sum.

    Raises ``ValueError`` at first access if the weights do not sum to 1.0
    within float tolerance — this is the 'fail fast at startup' requirement
    from §15.4, triggered on the first recommendation request.
    """
    settings = get_settings()
    path = Path(settings.RECOMMENDATION_CONFIG_PATH)
    if not path.is_absolute():
        # Resolve relative to the project root (GeoAI/)
        # weights.py is at app/domain/recommendation/weights.py
        # parents: [0]=recommendation, [1]=domain, [2]=app, [3]=backend, [4]=GeoAI
        path = Path(__file__).resolve().parents[4] / path

    with open(path) as f:
        raw = yaml.safe_load(f)

    weights = RecommendationWeights(
        distance=raw["distance_weight"],
        travel_time=raw["travel_time_weight"],
        crowd=raw["crowd_weight"],
        rating=raw["rating_weight"],
        freshness=raw["freshness_weight"],
        suitability=raw["suitability_weight"],
    )

    total = (
        weights.distance
        + weights.travel_time
        + weights.crowd
        + weights.rating
        + weights.freshness
        + weights.suitability
    )
    if abs(total - 1.0) >= 0.001:
        raise ValueError(
            f"Recommendation weights must sum to 1.0 (got {total:.4f}). "
            f"Check {settings.RECOMMENDATION_CONFIG_PATH}."
        )

    return weights
