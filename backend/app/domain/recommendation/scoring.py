"""Six pure sub-score functions for the recommendation formula.

Each function is stateless, takes only the data it needs, and returns a
score in [0, 100].  No DB calls, no HTTP — perfectly unit-testable.
"""

from datetime import datetime


def distance_score(distance_m: float, radius_m: float) -> float:
    """§15.3 Distance: 100 × (1 − distance / radius)."""
    return max(0.0, 100.0 * (1.0 - distance_m / radius_m))


def travel_time_score(
    estimated_time_s: float, radius_m: float, walking_speed_mps: float
) -> float:
    """Travel Time: 100 × (1 − time / max_acceptable_time).

    max_acceptable_time is derived from radius_m / walking_speed_mps
    (decision #4) so Distance and Travel Time normalise against the
    same request-specific bound.
    """
    max_acceptable = radius_m / walking_speed_mps
    return max(0.0, 100.0 * (1.0 - estimated_time_s / max_acceptable))


def freshness_score(
    status_updated_at: datetime, now: datetime, horizon_hours: float
) -> float:
    """§15.3 Freshness: 100 × (1 − hours_since_update / horizon)."""
    hours_since = (now - status_updated_at).total_seconds() / 3600.0
    return max(0.0, 100.0 * (1.0 - hours_since / horizon_hours))


def crowd_score(predicted_usage: float, effective_capacity: float) -> float:
    """§15.3 Crowd: 100 × (1 − predicted_usage / capacity), clamped [0,100]."""
    normalized = predicted_usage / effective_capacity
    return max(0.0, min(100.0, 100.0 * (1.0 - normalized)))


def rating_score(rating: float | None) -> float:
    """§15.3 Rating: (rating / 5) × 100, neutral 50 when missing."""
    return (rating / 5.0) * 100.0 if rating is not None else 50.0


def suitability_score(
    accessibility: dict | None,
    secondary_preference: str | None,
    penalty: float,
) -> float:
    """§15.3 Suitability: 100 if preference met or no preference; penalty otherwise.

    Only ``"wheelchair_accessible"`` is recognised — any other value is
    treated as no preference (graceful degradation, decision #6).
    """
    if secondary_preference != "wheelchair_accessible":
        return 100.0
    is_accessible = bool(
        (accessibility or {}).get("wheelchair_friendly", False)
    )
    return 100.0 if is_accessible else penalty
