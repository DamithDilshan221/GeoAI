from app.domain.entities import Category
from app.repositories.category_repository import CategoryRepository


class CategoryService:
    def __init__(self, category_repo: CategoryRepository):
        self._category_repo = category_repo

    def list_active(self) -> list[Category]:
        """Return all active categories ordered by label."""
        return self._category_repo.list_active()
