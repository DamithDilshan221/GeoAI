"""RecommendationLog ORM model (spec §18.5)."""

import uuid
from datetime import datetime
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class RecommendationLog(Base):
    """Audit log for each facility surfaced in a recommendation response."""

    __tablename__ = "recommendation_logs"

    id: Mapped[int] = mapped_column(sa.BigInteger, primary_key=True, autoincrement=True)
    request_id: Mapped[uuid.UUID] = mapped_column(sa.Uuid, nullable=False)
    facility_id: Mapped[int | None] = mapped_column(
        sa.BigInteger,
        sa.ForeignKey("facilities.id", ondelete="SET NULL"),
        nullable=True,
    )
    category_id: Mapped[int | None] = mapped_column(
        sa.SmallInteger,
        sa.ForeignKey("categories.id"),
        nullable=True,
    )
    user_lat_rounded: Mapped[Decimal | None] = mapped_column(sa.Numeric(5, 3), nullable=True)
    user_lon_rounded: Mapped[Decimal | None] = mapped_column(sa.Numeric(6, 3), nullable=True)
    radius_m: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)
    distance_m: Mapped[Decimal | None] = mapped_column(sa.Numeric, nullable=True)
    predicted_usage: Mapped[Decimal | None] = mapped_column(sa.Numeric, nullable=True)
    prediction_source: Mapped[str | None] = mapped_column(sa.String(16), nullable=True)
    recommendation_score: Mapped[Decimal | None] = mapped_column(sa.Numeric, nullable=True)
    rank_position: Mapped[int | None] = mapped_column(sa.SmallInteger, nullable=True)
    was_top_recommendation: Mapped[bool] = mapped_column(
        sa.Boolean, nullable=False, server_default=sa.text("false")
    )
    model_version: Mapped[str | None] = mapped_column(
        sa.String(32), nullable=True
    )  # Soft reference — no FK constraint
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
    )
