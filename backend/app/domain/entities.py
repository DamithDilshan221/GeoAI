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
from datetime import date, datetime
from typing import Literal

from app.models.enums import AudienceType, DataSource, FacilityStatus


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
    audience: AudienceType
    location_name: str | None
    fixtures: dict
    total_stalls: int
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
    """A facility with a computed distance from a search origin."""

    id: int
    name: str
    category_code: str
    audience: AudienceType
    status: FacilityStatus
    rating: float | None
    fixtures: dict
    distance_m: float
    latitude: float
    longitude: float


@dataclass(frozen=True)
class RouteResult:
    """The result of a routing calculation between an origin and a facility."""

    distance_m: float
    estimated_time_s: int
    path: list[tuple[float, float]]  # (lat, lon) pairs IN ORDER
    source: Literal["network", "straight_line_estimate"]


@dataclass(frozen=True)
class UsageRecord:
    id: int
    facility_id: int
    date: date
    hour: int
    day_of_week: int
    usage_count: int
    selection_count: int
    data_source: DataSource
