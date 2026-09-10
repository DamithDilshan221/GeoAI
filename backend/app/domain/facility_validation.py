"""Pure validation functions for facility input data (spec §11, §8).

These functions are completely framework-free — no SQLAlchemy, no FastAPI,
no database connection required.  They can be (and are) tested in isolation
with Postgres stopped.

Design note: the checks here deliberately duplicate the database CHECK
constraints defined in the Phase 2 migration (rating BETWEEN 0 AND 5,
capacity > 0, etc.).  That duplication is intentional — this layer gives a
fast, aggregated, human-readable error message *before* we pay the cost of a
round-trip to the DB.  The DB constraints remain the authoritative source of
truth; if they ever diverge, the DB wins.

``validate_facility_input`` does NOT check that ``category_id`` references a
real category — that requires a DB query and is the repository's responsibility
(see ``FacilityRepository.create``).
"""

from __future__ import annotations

VALID_FIXTURE_KEYS = {"attached", "normal", "shower", "sink", "mirror"}


def validate_fixtures(fixtures: dict) -> list[str]:
    """Returns a list of error strings (empty if valid) -- aggregate,
    same pattern as the rest of this file's validation, don't
    short-circuit on the first problem."""
    errors = []
    for key, value in fixtures.items():
        if key not in VALID_FIXTURE_KEYS:
            errors.append(f"unknown fixture key '{key}'")
        elif not isinstance(value, int) or value < 0:
            errors.append(f"fixture '{key}' must be a non-negative integer, got {value!r}")
    return errors


class FacilityValidationError(Exception):
    """Raised when one or more facility input fields are invalid.

    All violations are collected before raising so callers receive a complete
    picture in a single exception rather than having to fix-and-retry for each
    individual problem.
    """

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__("; ".join(errors))


def validate_facility_input(
    *,
    name: str,
    location_name: str,
    latitude: float,
    longitude: float,
    rating: float | None = None,
    fixtures: dict | None = None,
) -> None:
    """Validate facility input fields, collecting ALL violations before raising.

    Args:
        name: Facility name — must be non-empty and ≤ 200 characters.
        location_name: Building/place name — must be non-empty and ≤ 200 chars.
        latitude: Geographic latitude — must be in [-90, 90].
        longitude: Geographic longitude — must be in [-180, 180].
        rating: Optional star rating — if provided, must be in [0, 5].
        fixtures: Optional fixtures dict — valid keys only, non-negative ints.

    Raises:
        FacilityValidationError: If any field fails validation.  The
            ``errors`` attribute lists every violation found.
    """
    errors: list[str] = []

    # ── Name ────────────────────────────────────────────────────────────────
    # Mirrors facilities.name VARCHAR(200) NOT NULL (spec §18.3)
    if not name or not name.strip():
        errors.append("name must not be empty")
    elif len(name) > 200:
        errors.append(f"name must be ≤ 200 characters (got {len(name)})")

    # ── Location Name ───────────────────────────────────────────────────────
    if not location_name or not location_name.strip():
        errors.append("location_name must not be empty")
    elif len(location_name) > 200:
        errors.append(f"location_name must be ≤ 200 characters (got {len(location_name)})")

    # ── Latitude ─────────────────────────────────────────────────────────────
    if not (-90.0 <= latitude <= 90.0):
        errors.append(f"latitude must be in [-90, 90] (got {latitude})")

    # ── Longitude ────────────────────────────────────────────────────────────
    if not (-180.0 <= longitude <= 180.0):
        errors.append(f"longitude must be in [-180, 180] (got {longitude})")

    # ── Rating ───────────────────────────────────────────────────────────────
    # Mirrors CHECK (rating BETWEEN 0 AND 5) from Phase 2 migration
    if rating is not None and not (0.0 <= rating <= 5.0):
        errors.append(f"rating must be in [0, 5] (got {rating})")

    # ── Fixtures ─────────────────────────────────────────────────────────────
    if fixtures is not None:
        errors.extend(validate_fixtures(fixtures))

    if errors:
        raise FacilityValidationError(errors)
