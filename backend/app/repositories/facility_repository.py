"""Facility repository — sole owner of all SQL/ORM queries against ``facilities``.

No code outside this module may issue queries against the ``facilities`` table
directly (spec §11 layer rules).  All public methods return domain-layer
``Facility`` dataclasses, never raw ORM instances or SQL rows.

The ``create`` method is the only writer in the MVP; spec §16.2 has no
create/update/delete facility API endpoints, so no mutation methods beyond
``create`` are added (speculative unused surface area is explicitly excluded
by the Phase 3 non-goals).

Usage::

    with Session(engine) as session:
        repo = FacilityRepository(session)
        facility = repo.get_by_id(42)
        results  = repo.list(category_id=1, status=FacilityStatus.OPEN)
"""

from __future__ import annotations

from sqlalchemy.exc import DataError, IntegrityError
from sqlalchemy.orm import Session

from app.domain.entities import Facility as FacilityEntity
from app.domain.facility_validation import validate_facility_input
from app.models.enums import DataSource, FacilityStatus
from app.models.facility import Facility as FacilityORM
from app.repositories.exceptions import FacilityReferenceError

# The maximum number of rows list() will ever return, regardless of what the
# caller passes.  Cross-checked against spec §16.3 (max=50 for GET /facilities).
_MAX_LIMIT = 50


def _to_entity(orm: FacilityORM) -> FacilityEntity:
    """Map a SQLAlchemy ORM instance to the domain ``Facility`` dataclass.

    ``rating`` and ``capacity`` are stored as ``Decimal`` / ``int`` in the ORM
    but are converted to ``float`` / ``int`` here for ergonomic downstream use
    (JSON serialisation, arithmetic, etc.).  Precision is not lost because the
    DB column is Numeric(2,1) — one decimal place — which is fully representable
    as a float.
    """
    return FacilityEntity(
        id=orm.id,
        name=orm.name,
        category_id=orm.category_id,
        latitude=float(orm.latitude),
        longitude=float(orm.longitude),
        status=orm.status,
        status_updated_at=orm.status_updated_at,
        rating=float(orm.rating) if orm.rating is not None else None,
        capacity=orm.capacity,
        accessibility=orm.accessibility,
        data_source=orm.data_source,
        is_active=orm.is_active,
        created_at=orm.created_at,
        updated_at=orm.updated_at,
    )


class FacilityRepository:
    """Data-access object for the ``facilities`` table.

    All public methods accept and return plain Python objects; no SQLAlchemy
    types escape this class (spec §11).
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    # ── Queries ──────────────────────────────────────────────────────────────

    def get_by_id(
        self, facility_id: int, *, include_inactive: bool = False
    ) -> FacilityEntity | None:
        """Return the facility with the given primary key, or ``None``.

        Soft-deleted (``is_active=False``) rows are excluded by default, in
        line with spec §12.1's soft-delete policy.  Pass ``include_inactive=True``
        only when admin tooling explicitly needs to surface deactivated rows.

        Args:
            facility_id: The primary key of the facility.
            include_inactive: If ``True``, inactive rows are also considered.

        Returns:
            A ``Facility`` entity, or ``None`` if not found / excluded.
        """
        q = self._session.query(FacilityORM).filter(FacilityORM.id == facility_id)
        if not include_inactive:
            q = q.filter(FacilityORM.is_active.is_(True))
        row = q.one_or_none()
        return _to_entity(row) if row is not None else None

    def list(
        self,
        *,
        category_id: int | None = None,
        status: FacilityStatus | None = None,
        is_active: bool = True,
        limit: int = 25,
        offset: int = 0,
    ) -> list[FacilityEntity]:
        """Return a filtered, paginated list of facilities.

        Filters combine with AND.  ``limit`` is silently capped at
        ``_MAX_LIMIT`` (50) even if the caller requests more — cross-checked
        against spec §16.3's max=50 for GET /facilities.

        Args:
            category_id: If given, restrict to this category.
            status: If given, restrict to this operational status.
            is_active: Defaults to ``True`` (exclude soft-deleted rows).
            limit: Maximum rows to return; capped at 50.
            offset: Rows to skip for pagination.

        Returns:
            List of matching ``Facility`` entities (may be empty).
        """
        effective_limit = min(limit, _MAX_LIMIT)

        q = self._session.query(FacilityORM).filter(
            FacilityORM.is_active.is_(is_active)
        )
        if category_id is not None:
            q = q.filter(FacilityORM.category_id == category_id)
        if status is not None:
            q = q.filter(FacilityORM.status == status)

        rows = q.order_by(FacilityORM.id).limit(effective_limit).offset(offset).all()
        return [_to_entity(r) for r in rows]

    def _get_by_name(self, name: str) -> FacilityEntity | None:
        """Return the first facility matching ``name`` exactly, or ``None``.

        Used internally by the seed script for skip-if-exists logic.  Not
        exposed as a public API endpoint (no such route exists in spec §16.2).
        """
        row = (
            self._session.query(FacilityORM)
            .filter(FacilityORM.name == name)
            .first()
        )
        return _to_entity(row) if row is not None else None

    # ── Writers ──────────────────────────────────────────────────────────────

    def create(
        self,
        *,
        name: str,
        category_id: int,
        latitude: float,
        longitude: float,
        status: FacilityStatus = FacilityStatus.OPEN,
        rating: float | None = None,
        capacity: int | None = None,
        accessibility: dict | None = None,
        data_source: DataSource,
    ) -> FacilityEntity:
        """Insert a new facility and return the persisted domain entity.

        Steps (in order):
        1. Call ``validate_facility_input()`` — ``FacilityValidationError``
           propagates unchanged if any field is out of range.
        2. Attempt the ORM insert.  If the DB raises an ``IntegrityError``
           caused by the ``category_id`` FK constraint, catch it and raise
           ``FacilityReferenceError(category_id)`` so the caller never sees
           a raw SQLAlchemy error.
        3. ``flush()`` (not just ``add()``) so the ``before_insert`` event
           listener from Phase 2 (``_sync_geom``) has run and the row has a
           server-assigned ``id`` before we map it to a dataclass and return.

        Args:
            name: Facility name (≤ 200 chars, non-empty).
            category_id: FK reference to ``categories.id``.
            latitude: Geographic latitude in [-90, 90].
            longitude: Geographic longitude in [-180, 180].
            status: Operational status; defaults to ``OPEN``.
            rating: Optional star rating in [0, 5].
            capacity: Optional capacity count (must be > 0 if provided).
            accessibility: Optional JSON blob of accessibility features.
            data_source: Provenance of the record.

        Returns:
            The newly created ``Facility`` entity with all server-assigned
            fields (``id``, ``created_at``, ``updated_at``, etc.) populated.

        Raises:
            FacilityValidationError: If any input field fails validation.
            FacilityReferenceError: If ``category_id`` does not reference an
                existing category (FK violation).
        """
        # Step 1 — fail-fast validation before touching the DB
        validate_facility_input(
            name=name,
            latitude=latitude,
            longitude=longitude,
            rating=rating,
            capacity=capacity,
        )

        # Step 2 — insert; catch FK violations cleanly
        orm = FacilityORM(
            name=name,
            category_id=category_id,
            # latitude/longitude are stored on the ORM object;
            # the before_insert listener derives geom from them automatically.
            latitude=latitude,
            longitude=longitude,
            status=status,
            rating=rating,
            capacity=capacity,
            accessibility=accessibility,
            data_source=data_source,
        )
        self._session.add(orm)
        try:
            # Step 3 — flush so the event listener fires and id is assigned
            self._session.flush()
        except (IntegrityError, DataError) as exc:
            # IntegrityError → FK violation (category_id does not exist)
            # DataError     → value out of range for SMALLINT (category_id > 32767)
            # Both have the same semantic meaning for the caller: the referenced
            # category does not exist or is not addressable.
            self._session.rollback()
            raise FacilityReferenceError(category_id) from exc

        return _to_entity(orm)
