"""Category repository — sole owner of all SQL/ORM queries against ``categories``.

No code outside this module may issue queries against the ``categories`` table
directly (spec §11 layer rules).  All public methods return domain-layer
``Category`` dataclasses, never raw ORM instances.

Usage::

    with Session(engine) as session:
        repo = CategoryRepository(session)
        cats = repo.list_active()
        new  = repo.create(code="hospital", label="Hospital")
"""

from __future__ import annotations

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.entities import Category as CategoryEntity
from app.models.category import Category as CategoryORM
from app.repositories.exceptions import DuplicateCategoryCodeError


def _to_entity(orm: CategoryORM) -> CategoryEntity:
    """Map a SQLAlchemy ORM instance to the domain ``Category`` dataclass."""
    return CategoryEntity(
        id=orm.id,
        code=orm.code,
        label=orm.label,
        is_active=orm.is_active,
    )


class CategoryRepository:
    """Data-access object for the ``categories`` table.

    All public methods accept and return plain Python objects; no SQLAlchemy
    types escape this class (spec §11).
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    # ── Queries ──────────────────────────────────────────────────────────────

    def list_active(self) -> list[CategoryEntity]:
        """Return all active categories ordered alphabetically by label.

        Returns:
            List of ``Category`` entities where ``is_active`` is ``True``,
            sorted ascending by ``label``.
        """
        rows = (
            self._session.query(CategoryORM)
            .filter(CategoryORM.is_active.is_(True))
            .order_by(CategoryORM.label)
            .all()
        )
        return [_to_entity(r) for r in rows]

    def get_by_code(self, code: str) -> CategoryEntity | None:
        """Return the category with the given code, or ``None`` if absent.

        Args:
            code: The unique short code (e.g. ``"hospital"``).

        Returns:
            A ``Category`` entity, or ``None``.
        """
        row = (
            self._session.query(CategoryORM)
            .filter(CategoryORM.code == code)
            .one_or_none()
        )
        return _to_entity(row) if row is not None else None

    # ── Writers ──────────────────────────────────────────────────────────────

    def create(self, *, code: str, label: str) -> CategoryEntity:
        """Insert a new category and return the persisted domain entity.

        This method is used exclusively by the seed script.  A new category is
        created with ``is_active=True`` (the column default).

        Args:
            code: Unique short code (max 64 chars, matches the DB UNIQUE
                constraint on ``categories.code``).
            label: Human-readable display name (max 128 chars).

        Returns:
            The newly created ``Category`` entity with its server-assigned
            ``id``.

        Raises:
            DuplicateCategoryCodeError: If a category with ``code`` already
                exists, wrapping the raw ``IntegrityError`` from the DB.
        """
        orm = CategoryORM(code=code, label=label)
        self._session.add(orm)
        try:
            self._session.flush()
        except IntegrityError as exc:
            self._session.rollback()
            raise DuplicateCategoryCodeError(code) from exc
        return _to_entity(orm)
