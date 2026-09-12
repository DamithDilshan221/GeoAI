"""Integration tests for MLModelVersionRepository — Phase 16.

All tests run against the real ``geoai_test`` database via the rollback-
transaction ``db_session`` fixture established in Phase 2/3.  Each test
rolls back automatically so zero rows persist after the suite.

Phase 13's two read-side tests are retained verbatim at the bottom of this
file so the full repository surface is covered in one place.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.repositories.ml_model_version_repository import (
    MLModelVersionRepository,
    VersionAlreadyExistsError,
    VersionNotFoundError,
)

# ── Helpers ───────────────────────────────────────────────────────────────────

_NOW = datetime(2026, 9, 12, 8, 0, 0, tzinfo=UTC)

_FAKE_ARTIFACT = "/tmp/test_model.joblib"  # path value only — file need not exist for DB tests


def _make_repo(session: Session) -> MLModelVersionRepository:
    return MLModelVersionRepository(session)


def _create(session: Session, version: str, *, notes: str | None = None) -> None:
    """Convenience: insert a version with minimal valid fields."""
    repo = _make_repo(session)
    repo.create_version(
        version=version,
        algorithm="random_forest",
        trained_at=_NOW,
        feature_list=["hour", "day_of_week"],
        evaluation_metrics={
            "mae": 0.111, "r2": 0.94, "beats_heuristic": False, "heuristic_mae": 0.106
        },
        artifact_path=_FAKE_ARTIFACT,
        notes=notes,
    )


# ── create_version tests ──────────────────────────────────────────────────────


class TestCreateVersion:
    def test_inserts_with_is_active_false(self, db_session: Session) -> None:
        """Insertion always uses is_active=false — even for versions that will
        later be promoted. Insertion and promotion are separate steps (decision #2).
        """
        _create(db_session, "test-v1")

        row = db_session.execute(
            text("SELECT is_active FROM ml_model_versions WHERE version = 'test-v1'")
        ).one_or_none()

        assert row is not None, "Row was not inserted"
        assert row.is_active is False, "Newly created version must be is_active=false"

    def test_duplicate_version_raises_named_error(self, db_session: Session) -> None:
        """A second create_version() with the same version string raises
        VersionAlreadyExistsError — not a raw IntegrityError (decision #4).
        """
        _create(db_session, "test-duplicate")

        with pytest.raises(VersionAlreadyExistsError, match="already registered"):
            _create(db_session, "test-duplicate")

    def test_all_fields_stored_correctly(self, db_session: Session) -> None:
        """feature_list and evaluation_metrics are round-tripped as JSON."""
        repo = _make_repo(db_session)
        repo.create_version(
            version="test-fields",
            algorithm="ridge",
            trained_at=_NOW,
            feature_list=["hour", "day_of_week", "is_weekend"],
            evaluation_metrics={
                "mae": 0.20, "r2": 0.85, "beats_heuristic": True, "heuristic_mae": 0.22
            },
            artifact_path="/tmp/ridge.joblib",
            notes="integration test",
        )

        row = db_session.execute(
            text(
                "SELECT algorithm, artifact_path, notes, "
                "evaluation_metrics->>'beats_heuristic' AS bh "
                "FROM ml_model_versions WHERE version = 'test-fields'"
            )
        ).one()
        assert row.algorithm == "ridge"
        assert row.artifact_path == "/tmp/ridge.joblib"
        assert row.notes == "integration test"
        assert row.bh == "true"


# ── promote tests ─────────────────────────────────────────────────────────────


class TestPromote:
    def test_promote_activates_new_and_deactivates_old(self, db_session: Session) -> None:
        """The key demotion test: heuristic-v0 starts active, promote() switches
        to new version — heuristic-v0 must become is_active=false afterward.
        """
        # heuristic-v0 is seeded by migration 0003 as is_active=true
        repo = _make_repo(db_session)

        # Insert the candidate (still is_active=false at this point)
        _create(db_session, "candidate-v1")

        # Confirm heuristic-v0 is active before promotion
        before_heuristic = db_session.execute(
            text("SELECT is_active FROM ml_model_versions WHERE version = 'heuristic-v0'")
        ).scalar()
        assert before_heuristic is True

        # Confirm new version is inactive before promotion
        before_candidate = db_session.execute(
            text("SELECT is_active FROM ml_model_versions WHERE version = 'candidate-v1'")
        ).scalar()
        assert before_candidate is False

        # Promote
        repo.promote("candidate-v1")
        db_session.flush()

        # Now candidate must be active, heuristic must be inactive
        after_heuristic = db_session.execute(
            text("SELECT is_active FROM ml_model_versions WHERE version = 'heuristic-v0'")
        ).scalar()
        after_candidate = db_session.execute(
            text("SELECT is_active FROM ml_model_versions WHERE version = 'candidate-v1'")
        ).scalar()

        assert after_heuristic is False, "heuristic-v0 must be deactivated after promotion"
        assert after_candidate is True, "candidate-v1 must be active after promotion"

    def test_exactly_one_active_row_after_promote(self, db_session: Session) -> None:
        """Invariant: exactly one is_active=true row regardless of promotion."""
        repo = _make_repo(db_session)
        _create(db_session, "v-count-test")
        repo.promote("v-count-test")
        db_session.flush()

        count = db_session.execute(
            text("SELECT COUNT(*) FROM ml_model_versions WHERE is_active = true")
        ).scalar()
        assert count == 1

    def test_promote_nonexistent_raises_and_leaves_active_row_untouched(
        self, db_session: Session
    ) -> None:
        """Promoting an unregistered version raises VersionNotFoundError and
        must NOT accidentally deactivate the currently active row (heuristic-v0).
        """
        repo = _make_repo(db_session)

        with pytest.raises(VersionNotFoundError, match="does not exist"):
            repo.promote("ghost-version-that-was-never-inserted")

        # heuristic-v0 must still be active
        active = db_session.execute(
            text("SELECT is_active FROM ml_model_versions WHERE version = 'heuristic-v0'")
        ).scalar()
        assert active is True, "Failed promote must not deactivate the working active row"


# ── exists tests ──────────────────────────────────────────────────────────────


class TestExists:
    def test_returns_false_for_unknown_version(self, db_session: Session) -> None:
        assert _make_repo(db_session).exists("totally-unknown-xyz") is False

    def test_returns_true_for_seeded_heuristic(self, db_session: Session) -> None:
        assert _make_repo(db_session).exists("heuristic-v0") is True

    def test_returns_true_after_create_version(self, db_session: Session) -> None:
        _create(db_session, "exists-check-v1")
        assert _make_repo(db_session).exists("exists-check-v1") is True


# ── beats_heuristic=false — row exists but never activated (§15.12) ───────────


class TestNonPromotedVersion:
    def test_non_promoted_version_inserted_but_not_active(self, db_session: Session) -> None:
        """Direct proof of §15.12: a model that doesn't beat the heuristic is
        recorded (is_active=false) and the previously-active row remains active.
        This mirrors the real promote_model.py logic when beats_heuristic=False.
        """
        repo = _make_repo(db_session)

        # Synthetic manifest with beats_heuristic=false
        repo.create_version(
            version="loser-v1",
            algorithm="ridge",
            trained_at=_NOW,
            feature_list=["hour"],
            evaluation_metrics={
                "mae": 0.50, "r2": 0.20, "beats_heuristic": False, "heuristic_mae": 0.106
            },
            artifact_path=_FAKE_ARTIFACT,
        )
        # beats_heuristic is False — DO NOT call promote()

        loser_active = db_session.execute(
            text("SELECT is_active FROM ml_model_versions WHERE version = 'loser-v1'")
        ).scalar()
        heuristic_active = db_session.execute(
            text("SELECT is_active FROM ml_model_versions WHERE version = 'heuristic-v0'")
        ).scalar()

        assert loser_active is False, "Non-promoted version must remain is_active=false"
        assert heuristic_active is True, "heuristic-v0 must remain active when no promotion occurs"


# ── Phase 13 read-side tests (retained, unchanged) ────────────────────────────


class TestGetActiveVersion:
    def test_returns_active_version_string(self, db_session: Session) -> None:
        """Migration 0003 seeds heuristic-v0 as the active row."""
        repo = _make_repo(db_session)
        assert repo.get_active_version() == "heuristic-v0"

    def test_returns_none_when_no_active_row(self, db_session: Session) -> None:
        """With all rows deactivated, returns None — not an exception."""
        db_session.execute(text("UPDATE ml_model_versions SET is_active = false"))
        db_session.flush()

        repo = _make_repo(db_session)
        assert repo.get_active_version() is None
