"""UsageRecord ORM model — hourly-aggregated facility usage (spec §18.4)."""

from datetime import date, datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.enums import DataSource


class UsageRecord(Base):
    """Hourly-aggregated usage/selection counts per facility."""

    __tablename__ = "usage_records"
    __table_args__ = (
        sa.UniqueConstraint("facility_id", "date", "hour", name="uq_usage_bucket"),
        sa.Index("idx_usage_feature_lookup", "facility_id", "day_of_week", "hour"),
    )

    id: Mapped[int] = mapped_column(sa.BigInteger, primary_key=True, autoincrement=True)
    facility_id: Mapped[int] = mapped_column(
        sa.BigInteger,
        sa.ForeignKey("facilities.id"),
        nullable=False,
    )
    date: Mapped[date] = mapped_column(sa.Date, nullable=False)
    hour: Mapped[int] = mapped_column(
        sa.SmallInteger,
        sa.CheckConstraint("hour BETWEEN 0 AND 23", name="hour_range"),
        nullable=False,
    )
    day_of_week: Mapped[int] = mapped_column(
        sa.SmallInteger,
        sa.CheckConstraint("day_of_week BETWEEN 0 AND 6", name="day_of_week_range"),
        nullable=False,
    )
    usage_count: Mapped[int] = mapped_column(
        sa.Integer, nullable=False, server_default=sa.text("0")
    )
    selection_count: Mapped[int] = mapped_column(
        sa.Integer, nullable=False, server_default=sa.text("0")
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
