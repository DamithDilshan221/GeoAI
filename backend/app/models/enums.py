"""Python enums that map to Postgres ENUM types.

The ``create_type=False`` on ``sa.Enum(...)`` columns is required because the
Alembic migration creates the Postgres types explicitly via
``op.execute("CREATE TYPE ...")``.
"""

import enum


class FacilityStatus(enum.StrEnum):
    """Operational status of a facility."""

    OPEN = "OPEN"
    CLOSED = "CLOSED"
    TEMPORARILY_UNAVAILABLE = "TEMPORARILY_UNAVAILABLE"


class DataSource(enum.StrEnum):
    """Provenance of a data record."""

    REAL = "REAL"
    PUBLIC = "PUBLIC"
    SYNTHETIC = "SYNTHETIC"


class PathType(enum.StrEnum):
    """The type of a pedestrian path segment, affecting routing cost and accessibility."""

    SIDEWALK = "SIDEWALK"
    STAIRS = "STAIRS"
    RAMP = "RAMP"
    CORRIDOR = "CORRIDOR"
    CROSSING = "CROSSING"
