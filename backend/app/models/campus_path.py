"""Pedestrian path ORM model mapped to the pgRouting network."""

from datetime import datetime
from typing import Any

import sqlalchemy as sa
from geoalchemy2 import Geometry
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.enums import DataSource, PathType


class CampusPath(Base):
    """A segment of the pedestrian routing network."""

    __tablename__ = "campus_paths"
    __table_args__ = (
        sa.Index("idx_campus_paths_geom", "geom", postgresql_using="gist"),
        sa.Index("idx_campus_paths_source", "source"),
        sa.Index("idx_campus_paths_target", "target"),
    )

    id: Mapped[int] = mapped_column(sa.BigInteger, primary_key=True, autoincrement=True)
    
    # Deliberately Geometry (not Geography) because pgRouting core functions operate on geometry.
    geom: Mapped[Any] = mapped_column(
        Geometry(geometry_type="LINESTRING", srid=4326, spatial_index=False),
        nullable=False,
    )
    
    path_type: Mapped[PathType] = mapped_column(
        sa.Enum(PathType, name="path_type", create_type=False),
        nullable=False,
    )
    
    cost: Mapped[float] = mapped_column(sa.Double, nullable=False)
    reverse_cost: Mapped[float] = mapped_column(sa.Double, nullable=False)
    
    source: Mapped[int | None] = mapped_column(sa.BigInteger, nullable=True)
    target: Mapped[int | None] = mapped_column(sa.BigInteger, nullable=True)
    
    is_active: Mapped[bool] = mapped_column(
        sa.Boolean, nullable=False, server_default=sa.text("true")
    )
    
    data_source: Mapped[DataSource] = mapped_column(
        sa.Enum(DataSource, name="data_source", create_type=False),
        nullable=False,
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
