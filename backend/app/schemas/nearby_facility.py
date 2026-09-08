"""Pydantic schemas for the nearby facilities API."""

from pydantic import BaseModel

from app.domain.entities import NearbyFacility
from app.models.enums import FacilityStatus


class NearbyFacilityRead(BaseModel):
    """Schema for a facility returned by the spatial search endpoint.
    
    This is intentionally distinct from the standard FacilityRead, as it is a
    flat structure containing distance_m and is tailored for map/search clients
    rather than general-purpose CRUD.
    """

    id: int
    name: str
    category: str
    status: FacilityStatus
    rating: float | None
    distance_m: float
    latitude: float
    longitude: float

    @classmethod
    def from_domain(cls, item: NearbyFacility) -> "NearbyFacilityRead":
        return cls(
            id=item.id,
            name=item.name,
            category=item.category_code,
            status=item.status,
            rating=item.rating,
            distance_m=item.distance_m,
            latitude=item.latitude,
            longitude=item.longitude,
        )
