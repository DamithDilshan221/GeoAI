from datetime import datetime

from pydantic import BaseModel

from app.domain.entities import FacilityWithCategory
from app.models.enums import DataSource, FacilityStatus


class FacilityRead(BaseModel):
    id: int
    name: str
    category: str
    status: FacilityStatus
    status_updated_at: datetime
    rating: float | None
    capacity: int | None
    accessibility: dict | None
    data_source: DataSource
    latitude: float
    longitude: float

    @classmethod
    def from_domain(cls, item: FacilityWithCategory) -> "FacilityRead":
        """Explicit mapping function."""
        return cls(
            id=item.facility.id,
            name=item.facility.name,
            category=item.category_code,
            status=item.facility.status,
            status_updated_at=item.facility.status_updated_at,
            rating=item.facility.rating,
            capacity=item.facility.capacity,
            accessibility=item.facility.accessibility,
            data_source=item.facility.data_source,
            latitude=item.facility.latitude,
            longitude=item.facility.longitude,
        )


class FacilityListResponse(BaseModel):
    items: list[FacilityRead]
    limit: int
    offset: int
    total: int
