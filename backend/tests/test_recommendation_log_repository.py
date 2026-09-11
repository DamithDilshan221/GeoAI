"""Unit tests for RecommendationLogRepository against geoai_test.

Verifies:
  - Coordinate rounding to 3 decimal places (round(), not truncation)
  - One shared request_id groups multiple rows from the same call
  - was_top_recommendation stored faithfully as True / False
"""

import uuid

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.enums import AudienceType, DataSource, FacilityStatus
from app.models.facility import Facility
from app.repositories.recommendation_log_repository import RecommendationLogRepository


def _seed_category_and_facility(db_session: Session) -> tuple[int, int]:
    """Insert one category and one facility; return (category_id, facility_id)."""
    cat = Category(code="log_test", label="Log Test")
    db_session.add(cat)
    db_session.flush()

    fac = Facility(
        name="Log Facility",
        location_name="Log Block",
        category_id=cat.id,
        latitude=7.254,
        longitude=80.597,
        status=FacilityStatus.OPEN,
        audience=AudienceType.VISITOR,
        fixtures={},
        data_source=DataSource.SYNTHETIC,
    )
    db_session.add(fac)
    db_session.flush()
    return cat.id, fac.id


class TestRecommendationLogRepository:
    def test_coordinate_rounding_round_not_truncate(self, db_session: Session) -> None:
        """round(7.25456789, 3) == 7.255 and round(80.59651234, 3) == 80.597.

        This asserts the Python built-in rounding behaviour (round-half-to-even)
        produces 7.255 and 80.597, not truncation (which would give 7.254 / 80.596).
        """
        cat_id, fac_id = _seed_category_and_facility(db_session)
        repo = RecommendationLogRepository(db_session)
        request_id = uuid.uuid4()

        repo.log_candidate(
            request_id=request_id,
            facility_id=fac_id,
            category_id=cat_id,
            user_lat=7.25456789,
            user_lon=80.59651234,
            radius_m=1000,
            distance_m=150.0,
            predicted_usage=3.0,
            prediction_source="heuristic",
            recommendation_score=85.0,
            rank_position=1,
            was_top_recommendation=True,
            model_version="heuristic-v0",
        )

        row = db_session.execute(
            text("SELECT user_lat_rounded, user_lon_rounded FROM recommendation_logs "
                 "WHERE request_id = :rid"),
            {"rid": str(request_id)},
        ).one()

        # round(7.25456789, 3) → 7.255  (rounds UP — 5th digit is 5)
        # round(80.59651234, 3) → 80.597 (rounds UP — 4th digit is 5)
        assert float(row.user_lat_rounded) == pytest.approx(7.255)
        assert float(row.user_lon_rounded) == pytest.approx(80.597)

    def test_shared_request_id_groups_rows(self, db_session: Session) -> None:
        """Two rows with the same request_id are both retrievable via WHERE request_id."""
        cat_id, fac_id = _seed_category_and_facility(db_session)
        repo = RecommendationLogRepository(db_session)
        shared_id = uuid.uuid4()

        for position in (1, 2):
            repo.log_candidate(
                request_id=shared_id,
                facility_id=fac_id,
                category_id=cat_id,
                user_lat=7.2545,
                user_lon=80.5965,
                radius_m=1000,
                distance_m=100.0 * position,
                predicted_usage=2.0,
                prediction_source="heuristic",
                recommendation_score=90.0 - position * 10,
                rank_position=position,
                was_top_recommendation=(position == 1),
                model_version="heuristic-v0",
            )

        rows = db_session.execute(
            text("SELECT rank_position FROM recommendation_logs "
                 "WHERE request_id = :rid ORDER BY rank_position"),
            {"rid": str(shared_id)},
        ).all()

        assert len(rows) == 2
        assert [r.rank_position for r in rows] == [1, 2]

    def test_was_top_recommendation_stored_correctly(self, db_session: Session) -> None:
        """True/False round-trip faithfully to the boolean column."""
        cat_id, fac_id = _seed_category_and_facility(db_session)
        repo = RecommendationLogRepository(db_session)
        request_id = uuid.uuid4()

        repo.log_candidate(
            request_id=request_id,
            facility_id=fac_id,
            category_id=cat_id,
            user_lat=7.2545,
            user_lon=80.5965,
            radius_m=1000,
            distance_m=200.0,
            predicted_usage=5.0,
            prediction_source="heuristic",
            recommendation_score=75.0,
            rank_position=2,
            was_top_recommendation=False,
            model_version="heuristic-v0",
        )

        row = db_session.execute(
            text("SELECT was_top_recommendation FROM recommendation_logs "
                 "WHERE request_id = :rid"),
            {"rid": str(request_id)},
        ).one()

        assert row.was_top_recommendation is False

    def test_model_version_nullable(self, db_session: Session) -> None:
        """None model_version is stored as NULL, not as a string."""
        cat_id, fac_id = _seed_category_and_facility(db_session)
        repo = RecommendationLogRepository(db_session)
        request_id = uuid.uuid4()

        repo.log_candidate(
            request_id=request_id,
            facility_id=fac_id,
            category_id=cat_id,
            user_lat=7.2545,
            user_lon=80.5965,
            radius_m=1000,
            distance_m=300.0,
            predicted_usage=1.0,
            prediction_source="heuristic",
            recommendation_score=60.0,
            rank_position=1,
            was_top_recommendation=True,
            model_version=None,
        )

        row = db_session.execute(
            text("SELECT model_version FROM recommendation_logs WHERE request_id = :rid"),
            {"rid": str(request_id)},
        ).one()

        assert row.model_version is None
