"""Pure unit tests for facility input validation (spec §7, Phase 3).

No database connection is required — these tests import only from
``app.domain.facility_validation`` which has zero DB/ORM dependencies.
They can be run with Postgres stopped.
"""

from __future__ import annotations

import pytest

from app.domain.facility_validation import FacilityValidationError, validate_facility_input

# ── Helpers ───────────────────────────────────────────────────────────────────


def _valid_kwargs(**overrides):  # type: ignore[return]
    """Return a complete set of valid keyword args, optionally overridden."""
    defaults = {
        "name": "Test Facility",
        "latitude": 6.9271,
        "longitude": 79.8612,
        "rating": None,
        "location_name": "Test Location",
        "fixtures": {"normal": 2},
    }
    defaults.update(overrides)
    return defaults


# ── Happy path ────────────────────────────────────────────────────────────────


def test_valid_input_raises_nothing() -> None:
    """A fully valid input must not raise."""
    validate_facility_input(**_valid_kwargs())


def test_valid_input_with_rating_raises_nothing() -> None:
    validate_facility_input(**_valid_kwargs(rating=4.5))


def test_boundary_latitude_90_raises_nothing() -> None:
    validate_facility_input(**_valid_kwargs(latitude=90.0))


def test_boundary_latitude_minus_90_raises_nothing() -> None:
    validate_facility_input(**_valid_kwargs(latitude=-90.0))


def test_boundary_longitude_180_raises_nothing() -> None:
    validate_facility_input(**_valid_kwargs(longitude=180.0))


def test_boundary_longitude_minus_180_raises_nothing() -> None:
    validate_facility_input(**_valid_kwargs(longitude=-180.0))


def test_boundary_rating_zero_raises_nothing() -> None:
    validate_facility_input(**_valid_kwargs(rating=0.0))


def test_boundary_rating_five_raises_nothing() -> None:
    validate_facility_input(**_valid_kwargs(rating=5.0))





# ── Latitude validation ───────────────────────────────────────────────────────


def test_latitude_too_high_raises() -> None:
    """latitude > 90 must raise with the bad value in the message."""
    with pytest.raises(FacilityValidationError) as exc_info:
        validate_facility_input(**_valid_kwargs(latitude=90.1))
    assert "90.1" in str(exc_info.value)


def test_latitude_too_low_raises() -> None:
    """latitude < -90 must raise with the bad value in the message."""
    with pytest.raises(FacilityValidationError) as exc_info:
        validate_facility_input(**_valid_kwargs(latitude=-91.5))
    assert "-91.5" in str(exc_info.value)


# ── Longitude validation ──────────────────────────────────────────────────────


def test_longitude_too_high_raises() -> None:
    """longitude > 180 must raise with the bad value in the message."""
    with pytest.raises(FacilityValidationError) as exc_info:
        validate_facility_input(**_valid_kwargs(longitude=181.0))
    assert "181.0" in str(exc_info.value)


def test_longitude_too_low_raises() -> None:
    """longitude < -180 must raise with the bad value in the message."""
    with pytest.raises(FacilityValidationError) as exc_info:
        validate_facility_input(**_valid_kwargs(longitude=-200.0))
    assert "-200.0" in str(exc_info.value)


# ── Rating validation ─────────────────────────────────────────────────────────


def test_rating_too_high_raises() -> None:
    """rating = 5.5 must raise."""
    with pytest.raises(FacilityValidationError) as exc_info:
        validate_facility_input(**_valid_kwargs(rating=5.5))
    assert "5.5" in str(exc_info.value)


def test_rating_negative_raises() -> None:
    """rating = -0.1 must raise."""
    with pytest.raises(FacilityValidationError) as exc_info:
        validate_facility_input(**_valid_kwargs(rating=-0.1))
    assert "-0.1" in str(exc_info.value)





# ── Name validation ───────────────────────────────────────────────────────────


def test_empty_name_raises() -> None:
    """An empty name must raise."""
    with pytest.raises(FacilityValidationError):
        validate_facility_input(**_valid_kwargs(name=""))


def test_whitespace_only_name_raises() -> None:
    """A whitespace-only name must raise (treated as empty)."""
    with pytest.raises(FacilityValidationError):
        validate_facility_input(**_valid_kwargs(name="   "))


def test_name_at_200_chars_raises_nothing() -> None:
    """A 200-character name is at the limit and must not raise."""
    validate_facility_input(**_valid_kwargs(name="x" * 200))


def test_name_at_201_chars_raises() -> None:
    """A 201-character name exceeds the limit and must raise."""
    with pytest.raises(FacilityValidationError) as exc_info:
        validate_facility_input(**_valid_kwargs(name="x" * 201))
    assert "201" in str(exc_info.value)


# ── Error collection (all violations found, not just first) ──────────────────


def test_three_simultaneous_violations_all_reported() -> None:
    """An input with three bad fields must raise with all three messages.

    Proves that validation collects ALL errors before raising, not just the
    first one encountered (short-circuit behaviour would be a bug).
    """
    with pytest.raises(FacilityValidationError) as exc_info:
        validate_facility_input(
            name="",  # violation 1: empty name
            latitude=200.0,  # violation 2: out of range
            longitude=300.0,  # violation 3: out of range
            rating=None,
            location_name="",
            fixtures={"bad": 1},
        )
    error = exc_info.value
    assert len(error.errors) == 5, f"Expected 3 errors, got {len(error.errors)}: {error.errors}"
    combined = str(error)
    # Each violation message must appear in the combined string
    assert "name" in combined
    assert "200.0" in combined
    assert "300.0" in combined
    assert "location_name" in combined
    assert "bad" in combined


def test_two_violations_both_in_errors_list() -> None:
    """rating=5.5 and invalid fixtures together must yield exactly 2 errors."""
    with pytest.raises(FacilityValidationError) as exc_info:
        validate_facility_input(
            name="Fine Name",
            location_name="Test Location",
            latitude=6.9271,
            longitude=79.8612,
            rating=5.5,
            fixtures={"normal": -1},
        )
    assert len(exc_info.value.errors) == 2
