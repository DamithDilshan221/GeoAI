"""Facility ORM model with geom ↔ lat/lon synchronization (spec §18.3, §12.4).

``geom`` is the AUTHORITATIVE column for all spatial queries starting Phase 5.
``latitude`` and ``longitude`` are denormalized for cheap reads; they are always
derived from / kept in sync with ``geom`` via the ``before_insert`` and
``before_update`` ORM event listeners at the bottom of this file.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any

import sqlalchemy as sa
from geoalchemy2 import Geography, WKTElement
from sqlalchemy import event
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB

from app.models.base import Base
from app.models.enums import AudienceType, DataSource, FacilityStatus


class Facility(Base):
    """A geolocated facility (hospital, school, bank, park, etc.)."""

    __tablename__ = "facilities"
    __table_args__ = (
        sa.Index("idx_facilities_geom", "geom", postgresql_using="gist"),
        sa.Index("idx_facilities_category", "category_id"),
        sa.Index(
            "idx_facilities_open",
            "category_id",
            postgresql_where=sa.text("status = 'OPEN' AND is_active"),
        ),
    )

    id: Mapped[int] = mapped_column(sa.BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(sa.String(200), nullable=False)
    category_id: Mapped[int] = mapped_column(
        sa.SmallInteger,
        sa.ForeignKey("categories.id"),
        nullable=False,
    )
    geom: Mapped[Any] = mapped_column(
        Geography(geometry_type="POINT", srid=4326, spatial_index=False),
        nullable=False,
    )
    latitude: Mapped[Decimal] = mapped_column(sa.Numeric(9, 6), nullable=False)
    longitude: Mapped[Decimal] = mapped_column(sa.Numeric(9, 6), nullable=False)
    status: Mapped[FacilityStatus] = mapped_column(
        sa.Enum(FacilityStatus, name="facility_status", create_type=False),
        nullable=False,
        server_default=sa.text("'OPEN'"),
    )
    status_updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
    )
    rating: Mapped[Decimal | None] = mapped_column(
        sa.Numeric(2, 1),
        sa.CheckConstraint("rating BETWEEN 0 AND 5", name="rating_range"),
        nullable=True,
    )
    audience: Mapped[AudienceType] = mapped_column(
        sa.Enum(AudienceType, name="audience_type", create_type=False),
        nullable=False, default=AudienceType.VISITOR,
    )
    location_name: Mapped[str | None] = mapped_column(sa.String(200), nullable=True)
    fixtures: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    total_stalls: Mapped[int] = mapped_column(
        sa.Integer, sa.Computed(
            "COALESCE((fixtures->>'attached')::INT,0) + COALESCE((fixtures->>'normal')::INT,0)",
            persisted=True,
        ),
    )
    data_source: Mapped[DataSource] = mapped_column(
        sa.Enum(DataSource, name="data_source", create_type=False),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        sa.Boolean, nullable=False, server_default=sa.text("true")
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
    )


# ── Lat/lon ↔ geom synchronization (spec §12.4) ─────────────────────────
#
# geom remains authoritative for every spatial query starting Phase 5.
# These listeners exist purely so cheap reads don't need an ST_X/ST_Y
# extraction on every response — callers set latitude/longitude, and
# the ORM transparently derives geom from them before the flush.


def _sync_geom(_mapper: object, _connection: object, target: Facility) -> None:
    """Compute geom from latitude/longitude before INSERT or UPDATE."""
    if target.latitude is not None and target.longitude is not None:
        target.geom = WKTElement(f"POINT({target.longitude} {target.latitude})", srid=4326)


event.listens_for(Facility, "before_insert")(_sync_geom)
event.listens_for(Facility, "before_update")(_sync_geom)
