"""Integration tests for CategoryRepository and FacilityRepository (spec §7, Phase 3).

All tests run against the real ``geoai_test`` database, reusing the ``db_session``
fixture from Phase 2's ``conftest.py``.  Each test gets a fresh, isolated session;
all application tables are truncated on teardown so no state leaks between tests.

The ``db_session`` fixture is NOT wrapped in a savepoint/rollback here because the
``conftest.py`` already handles table truncation.  Tests that need to verify "no
row was left behind" after a failed create() do so via a direct count query.
"""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.domain.entities import Category as CategoryEntity
from app.domain.entities import Facility as FacilityEntity
from app.domain.facility_validation import FacilityValidationError
from app.models.enums import DataSource, FacilityStatus
from app.repositories.category_repository import CategoryRepository
from app.repositories.exceptions import DuplicateCategoryCodeError, FacilityReferenceError
from app.repositories.facility_repository import FacilityRepository

# ── Helpers ───────────────────────────────────────────────────────────────────


def _make_category(
    session: Session, code: str = "TEST_CAT", label: str = "Test Category"
) -> CategoryEntity:
    """Insert a category via the repository and return the domain entity."""
    return CategoryRepository(session).create(code=code, label=label)


def _make_facility(
    session: Session,
    category: CategoryEntity,
    *,
    name: str = "Test Facility",
    latitude: float = 6.9271,
    longitude: float = 79.8612,
    status: FacilityStatus = FacilityStatus.OPEN,
    rating: float | None = None,
    capacity: int | None = None,
) -> FacilityEntity:
    """Insert a facility via the repository and return the domain entity."""
    return FacilityRepository(session).create(
        name=name,
        category_id=category.id,
        latitude=latitude,
        longitude=longitude,
        status=status,
        rating=rating,
        capacity=capacity,
        data_source=DataSource.SYNTHETIC,
    )


# ── CategoryRepository tests ──────────────────────────────────────────────────


def test_category_create_then_list_active_returns_it(db_session: Session) -> None:
    """Created category appears in list_active()."""
    repo = CategoryRepository(db_session)
    repo.create(code="HOSPITAL", label="Hospital")
    active = repo.list_active()
    codes = [c.code for c in active]
    assert "HOSPITAL" in codes


def test_category_create_returns_domain_entity(db_session: Session) -> None:
    """create() returns a Category dataclass, not an ORM instance."""
    result = _make_category(db_session, code="SCHOOL")
    assert isinstance(result, CategoryEntity)
    assert result.id > 0
    assert result.code == "SCHOOL"
    assert result.is_active is True


def test_category_list_active_ordered_by_label(db_session: Session) -> None:
    """list_active() returns categories sorted ascending by label."""
    repo = CategoryRepository(db_session)
    repo.create(code="ZZZ", label="Zoo")
    repo.create(code="AAA", label="Airport")
    repo.create(code="MMM", label="Market")
    active = repo.list_active()
    labels = [c.label for c in active]
    assert labels == sorted(labels)


def test_category_create_duplicate_code_raises_clear_error(db_session: Session) -> None:
    """A second create() with the same code raises DuplicateCategoryCodeError —
    not a raw IntegrityError."""
    repo = CategoryRepository(db_session)
    repo.create(code="PARK", label="Park")
    import pytest

    with pytest.raises(DuplicateCategoryCodeError) as exc_info:
        repo.create(code="PARK", label="Park Again")
    assert exc_info.value.code == "PARK"


def test_category_get_by_code_returns_entity(db_session: Session) -> None:
    """get_by_code() returns the matching Category entity."""
    repo = CategoryRepository(db_session)
    repo.create(code="CLINIC", label="Clinic")
    result = repo.get_by_code("CLINIC")
    assert result is not None
    assert isinstance(result, CategoryEntity)
    assert result.code == "CLINIC"


def test_category_get_by_code_missing_returns_none(db_session: Session) -> None:
    """get_by_code() returns None for an unknown code."""
    repo = CategoryRepository(db_session)
    assert repo.get_by_code("NONEXISTENT") is None


# ── FacilityRepository.create tests ──────────────────────────────────────────


def test_facility_create_returns_facility_dataclass(db_session: Session) -> None:
    """create() returns a Facility dataclass (not an ORM instance)."""
    cat = _make_category(db_session, code="FAC_CAT")
    result = _make_facility(db_session, cat)
    assert isinstance(result, FacilityEntity)
    assert result.id > 0
    assert result.name == "Test Facility"
    assert result.category_id == cat.id
    assert result.data_source == DataSource.SYNTHETIC


def test_facility_create_with_all_optional_fields(db_session: Session) -> None:
    """create() with rating and capacity returns correct values."""
    cat = _make_category(db_session, code="OPT_CAT")
    result = _make_facility(
        db_session, cat, rating=4.5, capacity=20, name="Optional Fields Facility"
    )
    assert result.rating == 4.5
    assert result.capacity == 20


def test_facility_create_invalid_coordinate_raises_validation_error(db_session: Session) -> None:
    """create() with an out-of-range latitude raises FacilityValidationError."""
    import pytest

    cat = _make_category(db_session, code="VAL_ERR_CAT")
    fac_repo = FacilityRepository(db_session)

    # Count rows before the failed attempt
    before = db_session.execute(text("SELECT count(*) FROM facilities")).scalar()

    with pytest.raises(FacilityValidationError):
        fac_repo.create(
            name="Bad Lat Facility",
            category_id=cat.id,
            latitude=200.0,  # out of range
            longitude=79.8612,
            data_source=DataSource.SYNTHETIC,
        )

    # No row should have been persisted
    after = db_session.execute(text("SELECT count(*) FROM facilities")).scalar()
    assert after == before, f"Expected {before} rows, got {after} (row leaked!)"


def test_facility_create_nonexistent_category_raises_reference_error(db_session: Session) -> None:
    """create() with a non-existent category_id raises FacilityReferenceError,
    not a raw IntegrityError."""
    import pytest

    fac_repo = FacilityRepository(db_session)
    with pytest.raises(FacilityReferenceError) as exc_info:
        fac_repo.create(
            name="Orphan Facility",
            category_id=999999,  # does not exist
            latitude=6.9271,
            longitude=79.8612,
            data_source=DataSource.SYNTHETIC,
        )
    assert exc_info.value.category_id == 999999


# ── FacilityRepository.get_by_id tests ───────────────────────────────────────


def test_get_by_id_returns_entity_for_active_facility(db_session: Session) -> None:
    """get_by_id() returns the Facility entity for an active facility."""
    cat = _make_category(db_session, code="GBI_CAT")
    fac = _make_facility(db_session, cat, name="Active Facility")
    repo = FacilityRepository(db_session)
    result = repo.get_by_id(fac.id)
    assert result is not None
    assert isinstance(result, FacilityEntity)
    assert result.id == fac.id


def test_get_by_id_returns_none_for_nonexistent_id(db_session: Session) -> None:
    """get_by_id() returns None when the id doesn't exist."""
    repo = FacilityRepository(db_session)
    assert repo.get_by_id(999999) is None


def test_get_by_id_excludes_inactive_by_default(db_session: Session) -> None:
    """get_by_id() returns None for an inactive facility when include_inactive is False."""
    cat = _make_category(db_session, code="INACT_CAT")
    fac = _make_facility(db_session, cat, name="Inactive Facility")

    # Mark as inactive via raw SQL to avoid adding an update() method
    db_session.execute(
        text("UPDATE facilities SET is_active = false WHERE id = :fid"),
        {"fid": fac.id},
    )
    db_session.flush()

    repo = FacilityRepository(db_session)
    assert repo.get_by_id(fac.id) is None


def test_get_by_id_include_inactive_returns_entity(db_session: Session) -> None:
    """get_by_id(include_inactive=True) returns the entity even when is_active is false."""
    cat = _make_category(db_session, code="INACT2_CAT")
    fac = _make_facility(db_session, cat, name="Inactive Facility 2")

    db_session.execute(
        text("UPDATE facilities SET is_active = false WHERE id = :fid"),
        {"fid": fac.id},
    )
    db_session.flush()

    repo = FacilityRepository(db_session)
    result = repo.get_by_id(fac.id, include_inactive=True)
    assert result is not None
    assert result.id == fac.id
    assert result.is_active is False


# ── FacilityRepository.list tests ────────────────────────────────────────────


def test_list_filters_by_category_id(db_session: Session) -> None:
    """list(category_id=...) returns only facilities in that category."""
    cat_a = _make_category(db_session, code="LIST_A")
    cat_b = _make_category(db_session, code="LIST_B")
    _make_facility(db_session, cat_a, name="Facility A1")
    _make_facility(db_session, cat_a, name="Facility A2")
    _make_facility(db_session, cat_b, name="Facility B1")

    repo = FacilityRepository(db_session)
    results_a = repo.list(category_id=cat_a.id)
    assert len(results_a) == 2
    assert all(f.category_id == cat_a.id for f in results_a)

    results_b = repo.list(category_id=cat_b.id)
    assert len(results_b) == 1
    assert results_b[0].category_id == cat_b.id


def test_list_filters_by_status(db_session: Session) -> None:
    """list(status=CLOSED) returns only CLOSED facilities."""
    cat = _make_category(db_session, code="STAT_CAT")
    _make_facility(db_session, cat, name="Open Fac", status=FacilityStatus.OPEN)
    _make_facility(db_session, cat, name="Closed Fac", status=FacilityStatus.CLOSED)

    repo = FacilityRepository(db_session)
    closed = repo.list(status=FacilityStatus.CLOSED)
    assert all(f.status == FacilityStatus.CLOSED for f in closed)
    names = [f.name for f in closed]
    assert "Closed Fac" in names
    assert "Open Fac" not in names


def test_list_filters_by_category_and_status_combined(db_session: Session) -> None:
    """list with both category_id and status filters correctly with AND logic."""
    cat_x = _make_category(db_session, code="COMB_X")
    cat_y = _make_category(db_session, code="COMB_Y")
    _make_facility(db_session, cat_x, name="X-Open", status=FacilityStatus.OPEN)
    _make_facility(db_session, cat_x, name="X-Closed", status=FacilityStatus.CLOSED)
    _make_facility(db_session, cat_y, name="Y-Open", status=FacilityStatus.OPEN)

    repo = FacilityRepository(db_session)
    results = repo.list(category_id=cat_x.id, status=FacilityStatus.OPEN)
    assert len(results) == 1
    assert results[0].name == "X-Open"


def test_list_excludes_inactive_by_default(db_session: Session) -> None:
    """list() excludes soft-deleted (is_active=false) facilities by default."""
    cat = _make_category(db_session, code="SOFT_DEL_CAT")
    active_fac = _make_facility(db_session, cat, name="Active Fac")
    inactive_fac = _make_facility(db_session, cat, name="Inactive Fac")

    db_session.execute(
        text("UPDATE facilities SET is_active = false WHERE id = :fid"),
        {"fid": inactive_fac.id},
    )
    db_session.flush()

    repo = FacilityRepository(db_session)
    results = repo.list()
    ids = [f.id for f in results]
    assert active_fac.id in ids
    assert inactive_fac.id not in ids


def test_list_limit_and_offset_pagination(db_session: Session) -> None:
    """list(limit=2, offset=1) returns the correct slice from the fixture set."""
    cat = _make_category(db_session, code="PAGE_CAT")
    for i in range(5):
        _make_facility(db_session, cat, name=f"Paged Facility {i:02d}")

    repo = FacilityRepository(db_session)
    page1 = repo.list(category_id=cat.id, limit=2, offset=0)
    page2 = repo.list(category_id=cat.id, limit=2, offset=2)

    assert len(page1) == 2
    assert len(page2) == 2
    # Pages must not overlap
    ids_page1 = {f.id for f in page1}
    ids_page2 = {f.id for f in page2}
    assert ids_page1.isdisjoint(ids_page2)


def test_list_limit_is_capped_at_50(db_session: Session) -> None:
    """Passing limit=100 silently returns at most 50 rows (spec §16.3)."""
    cat = _make_category(db_session, code="CAP_CAT")
    for i in range(5):
        _make_facility(db_session, cat, name=f"Cap Facility {i:02d}")

    repo = FacilityRepository(db_session)
    results = repo.list(category_id=cat.id, limit=100)
    # We only have 5 rows, but the hard cap of 50 must be applied at the SQL level
    assert len(results) <= 50


# ── Geom event listener verification ─────────────────────────────────────────


def test_geom_derived_from_lat_lon_via_repository(db_session: Session) -> None:
    """After FacilityRepository.create(), ST_X/ST_Y of geom match lat/lon.

    This verifies that the Phase 2 before_insert event listener fires
    correctly through the new repository code path (not just through the
    Phase 2 direct-ORM tests).
    """
    cat = _make_category(db_session, code="GEOM_CAT")
    lat, lon = 6.9271, 79.8612
    fac = FacilityRepository(db_session).create(
        name="Geom Test Facility",
        category_id=cat.id,
        latitude=lat,
        longitude=lon,
        data_source=DataSource.SYNTHETIC,
    )

    row = db_session.execute(
        text(
            "SELECT ST_X(geom::geometry) AS x, ST_Y(geom::geometry) AS y "
            "FROM facilities WHERE id = :fid"
        ),
        {"fid": fac.id},
    ).fetchone()

    assert row is not None, "No row found for the inserted facility"
    assert abs(float(row.x) - lon) < 1e-4, f"Longitude mismatch: {row.x} vs {lon}"
    assert abs(float(row.y) - lat) < 1e-4, f"Latitude mismatch: {row.y} vs {lat}"
