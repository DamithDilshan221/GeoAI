"""Service for nearby spatial search."""

from app.domain.entities import NearbyFacility
from app.domain.gis.coordinate_validation import validate_coordinates
from app.repositories.category_repository import CategoryRepository
from app.repositories.gis_repository import GISRepository
from app.models.enums import AudienceType


class NearbySearchService:
    def __init__(self, gis_repo: GISRepository, category_repo: CategoryRepository):
        self.gis_repo = gis_repo
        self.category_repo = category_repo

    def find_nearby(
        self,
        *,
        category_code: str,
        audience: AudienceType | None,
        lat: float,
        lon: float,
        radius_m: int,
        limit: int,
    ) -> list[NearbyFacility]:
        """Find active, open facilities of a specific category within radius.

        Raises CoordinateValidationError if coordinates are out of bounds.
        Returns an empty list if the category_code does not resolve to an active category.
        """
        # 1. Validate coordinates
        validate_coordinates(lat=lat, lon=lon)

        # 2. Resolve category code
        category = self.category_repo.get_by_code(category_code)
        if category is None:
            return []

        # 3. Query GIS repository
        rows = self.gis_repo.find_nearby(
            category_id=category.id,
            audience=audience,
            lat=lat,
            lon=lon,
            radius_m=radius_m,
            limit=limit,
        )

        # 4. Map to domain entity, injecting the exact requested category code
        return [
            NearbyFacility(
                id=row.id,
                name=row.name,
                category_code=category_code,
                audience=row.audience,
                status=row.status,
                rating=row.rating,
                fixtures=row.fixtures,
                distance_m=row.distance_m,
                latitude=row.latitude,
                longitude=row.longitude,
            )
            for row in rows
        ]
