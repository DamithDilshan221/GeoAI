"""Category ORM model (spec §18.2)."""

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Category(Base):
    """Facility categories (e.g. hospital, school, bank, park)."""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(sa.SmallInteger, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(sa.String(64), unique=True, nullable=False)
    label: Mapped[str] = mapped_column(sa.String(128), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        sa.Boolean, nullable=False, server_default=sa.text("true")
    )
