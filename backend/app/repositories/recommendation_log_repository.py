"""Repository for writing recommendation_logs rows.

This is the single, authoritative place that privacy-rounding of user
coordinates happens before they are persisted — per resolved decision #1.
No other call site may round coordinates; all callers must pass raw values
and let this layer apply ``round(..., 3)`` (~100 m precision, matching the
``Numeric(5,3)``/``Numeric(6,3)`` column definitions from Phase 1's migration).
"""

import uuid

from sqlalchemy.orm import Session

from app.models.recommendation_log import RecommendationLog as RecommendationLogORM


class RecommendationLogRepository:
    """Data-access object for the ``recommendation_logs`` table.

    All writes go through ``log_candidate``; there are deliberately no read
    methods (§5.2 defers the admin analytics surface to a later phase).
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def log_candidate(
        self,
        *,
        request_id: uuid.UUID,
        facility_id: int,
        category_id: int,
        user_lat: float,
        user_lon: float,
        radius_m: int,
        distance_m: float,
        predicted_usage: float | None,
        prediction_source: str,
        recommendation_score: float,
        rank_position: int,
        was_top_recommendation: bool,
        model_version: str | None,
    ) -> None:
        """Insert one ``recommendation_logs`` row for a single scored candidate.

        Coordinates are rounded to 3 decimal places (~100 m) here — this is
        the ONE place that rounding happens, per resolved decision #1.
        Flushes but does not commit — the caller's request-scoped session
        lifecycle handles that, same as every other repository in this codebase.

        Args:
            request_id: Shared UUID for all rows from one ``get_recommendations`` call.
            facility_id: The facility that was scored.
            category_id: The category that was requested.
            user_lat: Raw (unrounded) user latitude — rounded here before storage.
            user_lon: Raw (unrounded) user longitude — rounded here before storage.
            radius_m: Search radius in metres as supplied by the caller.
            distance_m: Straight-line or routed distance from user to facility.
            predicted_usage: Heuristic/ML predicted occupancy, or None if unavailable.
            prediction_source: ``"heuristic"`` or ``"ml_model"``.
            recommendation_score: Weighted final score in [0, 100].
            rank_position: 1-indexed position in the ranked list (1 = top).
            was_top_recommendation: True iff this row is the winning candidate.
            model_version: Active ``ml_model_versions.version`` string, or None.
        """
        orm = RecommendationLogORM(
            request_id=request_id,
            facility_id=facility_id,
            category_id=category_id,
            user_lat_rounded=round(user_lat, 3),
            user_lon_rounded=round(user_lon, 3),
            radius_m=radius_m,
            distance_m=distance_m,
            predicted_usage=predicted_usage,
            prediction_source=prediction_source,
            recommendation_score=recommendation_score,
            rank_position=rank_position,
            was_top_recommendation=was_top_recommendation,
            model_version=model_version,
        )
        self._session.add(orm)
        self._session.flush()
