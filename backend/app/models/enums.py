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


class AudienceType(enum.StrEnum):
    """Target audience for a facility."""

    VISITOR = "VISITOR"
    STAFF = "STAFF"
