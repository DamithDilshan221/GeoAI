"""Repository for spatial queries."""

from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.enums import AudienceType, FacilityStatus


@dataclass(frozen=True)
class NearbyFacilityRow:
    id: int
    name: str
    audience: AudienceType
    status: FacilityStatus
    rating: float | None
    fixtures: dict
    distance_m: float
    latitude: float
    longitude: float


class GISRepository:
    def __init__(self, session: Session):
        self.session = session

    def find_nearby(
        self,
        *,
        category_id: int,
        audience: AudienceType | None,
        lat: float,
        lon: float,
        radius_m: int,
        limit: int,
    ) -> list[NearbyFacilityRow]:
        """Find active, open facilities of a specific category within radius.

        Returns a list of NearbyFacilityRow objects ordered by distance.
        """
        query = text(
            """
            SELECT f.id, f.name, f.category_id, f.audience, f.status, f.rating, f.fixtures,
                   ST_Distance(f.geom, ST_MakePoint(:lon, :lat)::geography) AS distance_m,
                   f.latitude, f.longitude
            FROM facilities f
            WHERE f.is_active
              AND f.category_id = :category_id
              AND (:audience IS NULL OR f.audience = :audience)
              AND f.status = 'OPEN'
              AND ST_DWithin(f.geom, ST_MakePoint(:lon, :lat)::geography, :radius_m)
            ORDER BY distance_m ASC
            LIMIT :limit;
            """
        )

        result = self.session.execute(
            query,
            {
                "category_id": category_id,
                "audience": audience,
                "lat": lat,
                "lon": lon,
                "radius_m": radius_m,
                "limit": limit,
            },
        )

        return [
            NearbyFacilityRow(
                id=row.id,
                name=row.name,
                audience=AudienceType(row.audience),
                status=FacilityStatus(row.status),
                rating=row.rating,
                fixtures=row.fixtures,
                distance_m=float(row.distance_m),
                latitude=float(row.latitude),
                longitude=float(row.longitude),
            )
            for row in result
        ]
