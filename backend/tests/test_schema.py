"""Phase 2 schema verification tests.

Each test function verifies a specific constraint, index, or behavior
described in spec §18 against the real ``geoai_test`` database.
"""

import sys
import uuid
from datetime import date
from decimal import Decimal

import pytest
import sqlalchemy as sa
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import (
    Category,
    DataSource,
    Facility,
    FacilityStatus,
    MLModelVersion,
    RecommendationLog,
    UsageRecord,
)

# ── Helpers ──────────────────────────────────────────────────────────────


def _make_category(session: Session, code: str = "HOSPITAL") -> Category:
    """Insert and flush a Category, returning the persisted object."""
    cat = Category(code=code, label=f"Test {code}")
    session.add(cat)
    session.flush()
    return cat


def _make_facility(
    session: Session,
    category: Category,
    *,
    latitude: Decimal = Decimal("6.927079"),
    longitude: Decimal = Decimal("79.861244"),
    rating: Decimal | None = None,
    status: FacilityStatus = FacilityStatus.OPEN,
) -> Facility:
    """Insert and flush a Facility, returning the persisted object."""
    fac = Facility(
        name="Test Facility",
        category_id=category.id,
        latitude=latitude,
        longitude=longitude,
        rating=rating,
        data_source=DataSource.SYNTHETIC,
        status=status,
    )
    session.add(fac)
    session.flush()
    return fac


# ── Table existence ──────────────────────────────────────────────────────


def test_all_five_tables_exist_with_expected_columns(db_session: Session) -> None:
    """All five tables exist with their specified columns."""
    inspector = inspect(db_session.bind)
    expected_tables = {
        "categories": {"id", "code", "label", "is_active"},
        "facilities": {
            "id",
            "name",
            "category_id",
            "geom",
            "latitude",
            "longitude",
            "status",
            "status_updated_at",
            "rating",
            "audience",
            "location_name",
            "fixtures",
            "total_stalls",
            "data_source",
            "is_active",
            "created_at",
            "updated_at",
        },
        "usage_records": {
            "id",
            "facility_id",
            "date",
            "hour",
            "day_of_week",
            "usage_count",
            "selection_count",
            "data_source",
            "created_at",
        },
        "recommendation_logs": {
            "id",
            "request_id",
            "facility_id",
            "category_id",
            "user_lat_rounded",
            "user_lon_rounded",
            "radius_m",
            "distance_m",
            "predicted_usage",
            "prediction_source",
            "recommendation_score",
            "rank_position",
            "was_top_recommendation",
            "model_version",
            "created_at",
        },
        "ml_model_versions": {
            "id",
            "version",
            "algorithm",
            "trained_at",
            "feature_list",
            "evaluation_metrics",
            "artifact_path",
            "is_active",
            "notes",
        },
    }

    actual_tables = inspector.get_table_names()
    for table_name, expected_cols in expected_tables.items():
        assert table_name in actual_tables, f"Missing table: {table_name}"
        actual_cols = {c["name"] for c in inspector.get_columns(table_name)}
        assert expected_cols <= actual_cols, (
            f"{table_name} missing columns: {expected_cols - actual_cols}"
        )


# ── Index verification ───────────────────────────────────────────────────


def test_idx_facilities_geom_is_gist(db_session: Session) -> None:
    """idx_facilities_geom must exist and use the GIST access method."""
    result = db_session.execute(
        text(
            "SELECT indexname, indexdef FROM pg_indexes "
            "WHERE tablename = 'facilities' AND indexname = 'idx_facilities_geom'"
        )
    ).fetchone()
    assert result is not None, "idx_facilities_geom does not exist"
    assert "using gist" in result[1].lower()


# ── ENUM constraint ──────────────────────────────────────────────────────


def test_invalid_status_enum_rejected(db_session: Session) -> None:
    """Inserting a facility with an invalid status string must fail."""
    cat = _make_category(db_session)
    # Use a savepoint so the expected error doesn't abort the outer txn
    db_session.begin_nested()
    with pytest.raises((IntegrityError, sa.exc.DataError, sa.exc.ProgrammingError)):
        db_session.execute(
            text(
                "INSERT INTO facilities "
                "(name, category_id, geom, latitude, longitude, status, data_source) "
                "VALUES (:name, :cat_id, ST_GeogFromText('POINT(79.86 6.93)'), "
                "6.93, 79.86, :status, 'SYNTHETIC')"
            ),
            {"name": "Bad", "cat_id": cat.id, "status": "INVALID_STATUS"},
        )
    # Savepoint is automatically rolled back by the exception


# ── CHECK constraint: rating ─────────────────────────────────────────────


def test_rating_check_constraint_rejects_out_of_range(db_session: Session) -> None:
    """rating = 5.5 must fail the CHECK (rating BETWEEN 0 AND 5)."""
    cat = _make_category(db_session, code="BANK")
    db_session.begin_nested()
    with pytest.raises(IntegrityError):
        _make_facility(db_session, cat, rating=Decimal("5.5"))


def test_rating_check_constraint_accepts_valid(db_session: Session) -> None:
    """rating = 4.5 must succeed."""
    cat = _make_category(db_session, code="SCHOOL")
    fac = _make_facility(db_session, cat, rating=Decimal("4.5"))
    assert fac.rating == Decimal("4.5")


# ── Geom ↔ lat/lon synchronization ──────────────────────────────────────


def test_geom_synced_from_lat_lon_on_insert(db_session: Session) -> None:
    """After ORM insert with lat/lon, ST_X/ST_Y of geom must match."""
    cat = _make_category(db_session, code="PARK")
    lat, lon = Decimal("6.927079"), Decimal("79.861244")
    fac = _make_facility(db_session, cat, latitude=lat, longitude=lon)

    row = db_session.execute(
        text(
            "SELECT ST_X(geom::geometry) AS x, ST_Y(geom::geometry) AS y "
            "FROM facilities WHERE id = :fid"
        ),
        {"fid": fac.id},
    ).fetchone()

    assert row is not None
    assert abs(float(row.x) - float(lon)) < 1e-4
    assert abs(float(row.y) - float(lat)) < 1e-4


# ── Unique constraint: usage_bucket ──────────────────────────────────────


def test_duplicate_usage_bucket_rejected(db_session: Session) -> None:
    """Two usage_records with the same (facility_id, date, hour) must fail."""
    cat = _make_category(db_session, code="CAFE")
    fac = _make_facility(db_session, cat)
    common = {
        "facility_id": fac.id,
        "date": date(2026, 1, 15),
        "hour": 10,
        "day_of_week": 3,
        "data_source": DataSource.SYNTHETIC,
    }
    db_session.add(UsageRecord(**common))
    db_session.flush()

    db_session.begin_nested()
    with pytest.raises(IntegrityError):
        db_session.add(UsageRecord(**common))
        db_session.flush()


# ── Partial unique index: single active ML model ────────────────────────


def test_only_one_active_ml_model_version(db_session: Session) -> None:
    """Two ml_model_versions rows with is_active=True must violate the index."""
    v1 = MLModelVersion(version="test-model-v1", is_active=True)
    db_session.add(v1)
    db_session.flush()

    db_session.begin_nested()
    with pytest.raises(IntegrityError):
        v2 = MLModelVersion(version="test-model-v2", is_active=True)
        db_session.add(v2)
        db_session.flush()


# ── ON DELETE SET NULL: recommendation_logs.facility_id ──────────────────


def test_delete_facility_sets_recommendation_log_facility_id_null(
    db_session: Session,
) -> None:
    """Deleting a facility must SET NULL on referencing recommendation_logs rows."""
    cat = _make_category(db_session, code="GYM")
    fac = _make_facility(db_session, cat)

    log = RecommendationLog(
        request_id=uuid.uuid4(),
        facility_id=fac.id,
        category_id=cat.id,
        was_top_recommendation=False,
    )
    db_session.add(log)
    db_session.flush()
    log_id = log.id

    # Delete the facility via raw SQL to trigger FK cascade
    db_session.execute(text("DELETE FROM facilities WHERE id = :fid"), {"fid": fac.id})
    db_session.flush()

    # The recommendation_log row must still exist with facility_id = NULL
    row = db_session.execute(
        text("SELECT facility_id FROM recommendation_logs WHERE id = :lid"),
        {"lid": log_id},
    ).fetchone()
    assert row is not None
    assert row.facility_id is None


import subprocess
from pathlib import Path


def test_alembic_migrations_apply_cleanly() -> None:
    backend_dir = Path(__file__).parent.parent
    result = subprocess.run(["alembic", "upgrade", "head"], cwd=backend_dir, capture_output=True, text=True)
    assert result.returncode == 0, f"Alembic upgrade failed: {result.stderr}"

def test_idx_facilities_audience_exists(db_session: Session) -> None:
    result = db_session.execute(
        text("SELECT indexname FROM pg_indexes WHERE tablename = 'facilities' AND indexname = 'idx_facilities_audience'")
    ).fetchone()
    assert result is not None, "idx_facilities_audience does not exist"

def test_total_stalls_generated_column_computation(db_session: Session) -> None:
    cat = _make_category(db_session, code="WASH1")
    db_session.execute(
        text("INSERT INTO facilities (name, category_id, geom, latitude, longitude, fixtures, data_source) "
             "VALUES ('Washroom A', :cat_id, ST_GeogFromText('POINT(79.86 6.93)'), 6.93, 79.86, '{\"attached\": 2, \"normal\": 4}'::jsonb, 'SYNTHETIC')"),
        {"cat_id": cat.id}
    )
    fac_id = db_session.execute(text("SELECT id FROM facilities WHERE name = 'Washroom A'")).scalar()

    row = db_session.execute(text("SELECT total_stalls FROM facilities WHERE id = :fid"), {"fid": fac_id}).fetchone()
    assert row is not None
    assert row.total_stalls == 6

def test_total_stalls_generated_column_default(db_session: Session) -> None:
    cat = _make_category(db_session, code="WASH2")
    db_session.execute(
        text("INSERT INTO facilities (name, category_id, geom, latitude, longitude, data_source) "
             "VALUES ('Washroom B', :cat_id, ST_GeogFromText('POINT(79.86 6.93)'), 6.93, 79.86, 'SYNTHETIC')"),
        {"cat_id": cat.id}
    )
    fac_id = db_session.execute(text("SELECT id FROM facilities WHERE name = 'Washroom B'")).scalar()

    row = db_session.execute(text("SELECT total_stalls FROM facilities WHERE id = :fid"), {"fid": fac_id}).fetchone()
    assert row is not None
    assert row.total_stalls == 0

def test_total_stalls_direct_insert_fails(db_session: Session) -> None:
    cat = _make_category(db_session, code="WASH3")
    db_session.begin_nested()
    with pytest.raises(sa.exc.ProgrammingError):
        db_session.execute(
            text("INSERT INTO facilities (name, category_id, geom, latitude, longitude, total_stalls, data_source) "
                 "VALUES ('Washroom C', :cat_id, ST_GeogFromText('POINT(79.86 6.93)'), 6.93, 79.86, 10, 'SYNTHETIC')"),
            {"cat_id": cat.id}
        )

def test_location_name_accepts_null(db_session: Session) -> None:
    cat = _make_category(db_session, code="WASH4")
    db_session.execute(
        text("INSERT INTO facilities (name, category_id, geom, latitude, longitude, location_name, data_source) "
             "VALUES ('Washroom D', :cat_id, ST_GeogFromText('POINT(79.86 6.93)'), 6.93, 79.86, NULL, 'SYNTHETIC')"),
        {"cat_id": cat.id}
    )
    fac_id = db_session.execute(text("SELECT id FROM facilities WHERE name = 'Washroom D'")).scalar()
    row = db_session.execute(text("SELECT location_name FROM facilities WHERE id = :fid"), {"fid": fac_id}).fetchone()
    assert row is not None
    assert row.location_name is None

def test_campus_paths_no_longer_exists(db_session: Session) -> None:
    row = db_session.execute(
        text("SELECT table_name FROM information_schema.tables WHERE table_name = 'campus_paths'")
    ).fetchone()
    assert row is None

def test_alembic_downgrade_upgrade() -> None:
    backend_dir = Path(__file__).parent.parent

    res1 = subprocess.run([sys.executable, "-m", "alembic", "downgrade", "-1"], cwd=backend_dir, capture_output=True, text=True)
    assert res1.returncode == 0, f"Alembic downgrade -1 failed: {res1.stderr}"
    res2 = subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], cwd=backend_dir, capture_output=True, text=True)
    assert res2.returncode == 0, f"Alembic upgrade failed: {res2.stderr}"

    res3 = subprocess.run([sys.executable, "-m", "alembic", "downgrade", "-2"], cwd=backend_dir, capture_output=True, text=True)
    assert res3.returncode == 0, f"Alembic downgrade -2 failed: {res3.stderr}"
    res4 = subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], cwd=backend_dir, capture_output=True, text=True)
    assert res4.returncode == 0, f"Alembic upgrade failed: {res4.stderr}"
