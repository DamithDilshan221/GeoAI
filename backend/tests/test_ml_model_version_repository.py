"""Unit tests for MLModelVersionRepository against geoai_test.

The ``db_session`` fixture runs all Alembic migrations (including 0003 which
seeds the ``heuristic-v0`` row), so these tests can rely on that row being
present without additional seeding.
"""

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.repositories.ml_model_version_repository import MLModelVersionRepository


class TestMLModelVersionRepository:
    def test_returns_active_version_string(self, db_session: Session) -> None:
        """Migration 0003 seeds heuristic-v0 as the active row."""
        repo = MLModelVersionRepository(db_session)
        version = repo.get_active_version()
        assert version == "heuristic-v0"

    def test_returns_none_when_no_active_row(self, db_session: Session) -> None:
        """With all rows deactivated, returns None — not an exception.

        Mirrors the pattern used by test_ml_inference_service.py's
        test_ml_inference_service_no_active_provider.
        """
        db_session.execute(text("UPDATE ml_model_versions SET is_active = false"))
        db_session.flush()

        repo = MLModelVersionRepository(db_session)
        result = repo.get_active_version()

        assert result is None
