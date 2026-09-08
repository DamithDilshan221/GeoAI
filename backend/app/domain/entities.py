"""Domain entity dataclasses for the GeoAI facility layer (spec §11, §8).

These are plain, frozen Python dataclasses — completely separate from the
SQLAlchemy ORM models in ``app.models``.  Repositories map ORM rows to these
types before returning them; nothing above the repository layer ever sees a
raw ORM instance or a SQL result set.

Design note (spec §12.1): there is deliberately no ``geom`` field here.  All
spatial arithmetic (ST_DWithin, ST_Distance, etc.) happens inside PostGIS and
stays inside the repository layer.  Phase 5's spatial repository methods will
return a ``distance_m`` alongside the ``Facility`` entity; the shape of *this*
dataclass will not need to change for that.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.models.enums import DataSource, FacilityStatus


@dataclass(frozen=True)
class Category:
    """Immutable representation of a facility category (spec §18.2)."""

    id: int
    code: str
    label: str
    is_active: bool


@dataclass(frozen=True)
class Facility:
    """Immutable representation of a geolocated facility (spec §18.3).

    ``latitude`` and ``longitude`` are stored as plain ``float`` here (the ORM
    model uses ``Decimal`` for storage precision, but callers above the
    repository layer never do arithmetic on them directly — floats are
    sufficient and far more ergonomic for JSON serialisation).
    """

    id: int
    name: str
    category_id: int
    latitude: float
    longitude: float
    status: FacilityStatus
    status_updated_at: datetime
    rating: float | None
    capacity: int | None
    accessibility: dict | None
    data_source: DataSource
    is_active: bool
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class FacilityWithCategory:
    facility: Facility
    category_code: str
    category_label: str


@dataclass(frozen=True)
class NearbyFacility:
    id: int
    name: str
    category_code: str
    status: FacilityStatus
    rating: float | None
    distance_m: float
    latitude: float
    longitude: float

