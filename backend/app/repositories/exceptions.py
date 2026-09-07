"""Repository-layer exception types (spec §4, §8).

Raised by repository methods to give callers a clean, domain-meaningful error
instead of a raw SQLAlchemy ``IntegrityError`` or ``OperationalError``.
"""

from __future__ import annotations


class FacilityReferenceError(Exception):
    """Raised when a ``category_id`` foreign-key constraint is violated.

    The repository catches SQLAlchemy's raw ``IntegrityError`` on INSERT and
    re-raises this exception so that callers (services, API handlers) never
    have to inspect low-level DB exception strings.

    Attributes:
        category_id: The category ID that does not exist in the database.
    """

    def __init__(self, category_id: int) -> None:
        self.category_id = category_id
        super().__init__(f"category_id {category_id} does not exist")


class DuplicateCategoryCodeError(Exception):
    """Raised by ``CategoryRepository.create`` when the code already exists.

    Gives callers a clear, named error instead of a raw ``IntegrityError`` on
    the UNIQUE constraint of ``categories.code``.

    Attributes:
        code: The category code that already exists in the database.
    """

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(f"category with code '{code}' already exists")
