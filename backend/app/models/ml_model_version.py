"""MLModelVersion ORM model (spec §18.6).

The partial unique index ``uq_ml_model_versions_single_active`` enforces
at most one row with ``is_active = true`` at the database level.
"""

from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class MLModelVersion(Base):
    """Registered ML model versions (including the heuristic baseline)."""

    __tablename__ = "ml_model_versions"
    __table_args__ = (
        sa.Index(
            "uq_ml_model_versions_single_active",
            "is_active",
            unique=True,
            postgresql_where=sa.text("is_active"),
        ),
    )

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    version: Mapped[str] = mapped_column(sa.String(32), unique=True, nullable=False)
    algorithm: Mapped[str | None] = mapped_column(sa.String(64), nullable=True)
    trained_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    feature_list: Mapped[dict | None] = mapped_column(sa.JSON, nullable=True)
    evaluation_metrics: Mapped[dict | None] = mapped_column(sa.JSON, nullable=True)
    artifact_path: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(
        sa.Boolean, nullable=False, server_default=sa.text("false")
    )
    notes: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
