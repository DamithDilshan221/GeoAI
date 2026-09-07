from app.domain.entities import FacilityWithCategory
from app.models.enums import FacilityStatus
from app.repositories.category_repository import CategoryRepository
from app.repositories.facility_repository import FacilityRepository


class FacilityService:
    def __init__(
        self,
        facility_repo: FacilityRepository,
        category_repo: CategoryRepository,
    ):
        self._facility_repo = facility_repo
        self._category_repo = category_repo

    def _resolve_category_code(self, category_id: int) -> tuple[str, str]:
        """Look up code and label.

        Note: We fetch all active categories since there are very few,
        to avoid N+1 queries. In a real system we'd cache this or
        batch-fetch only the requested ones.
        """
        categories = self._category_repo.list_active()
        for c in categories:
            if c.id == category_id:
                return c.code, c.label
        return "unknown", "Unknown Category"

    def get_by_id(self, facility_id: int) -> FacilityWithCategory | None:
        """Returns None if not found or soft-deleted."""
        facility = self._facility_repo.get_by_id(facility_id)
        if not facility:
            return None

        code, label = self._resolve_category_code(facility.category_id)
        return FacilityWithCategory(
            facility=facility,
            category_code=code,
            category_label=label,
        )

    def list(
        self,
        *,
        category_code: str | None,
        status: FacilityStatus | None,
        limit: int,
        offset: int,
    ) -> tuple[list[FacilityWithCategory], int]:
        """Return a tuple of (items, total)."""
        category_id = None
        if category_code is not None:
            cat = self._category_repo.get_by_code(category_code)
            if not cat:
                # category_code provided but doesn't exist.
                return [], 0
            category_id = cat.id

        items = self._facility_repo.list(
            category_id=category_id,
            status=status,
            limit=limit,
            offset=offset,
        )
        total = self._facility_repo.count(
            category_id=category_id,
            status=status,
        )

        results = []
        for facility in items:
            code, label = self._resolve_category_code(facility.category_id)
            results.append(
                FacilityWithCategory(
                    facility=facility,
                    category_code=code,
                    category_label=label,
                )
            )

        return results, total
