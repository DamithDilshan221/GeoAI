"""Router for nearby spatial search endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.v1.dependencies import get_nearby_search_service
from app.domain.gis.exceptions import CoordinateValidationError
from app.domain.gis.nearby_search_service import NearbySearchService
from app.schemas.nearby_facility import NearbyFacilityRead

router = APIRouter(tags=["Facilities"])


@router.get("/facilities/nearby", response_model=list[NearbyFacilityRead])
def get_nearby_facilities(
    lat: float = Query(...),
    lon: float = Query(...),
    category: str = Query(...),
    radius_m: int = Query(default=1000, ge=1, le=10000),
    limit: int = Query(default=25, ge=1, le=50),
    service: NearbySearchService = Depends(get_nearby_search_service),  # noqa: B008
) -> list[NearbyFacilityRead]:
    """Search for nearby facilities.

    Returns a flat array of OPEN, active facilities of the requested category,
    ordered by distance from the provided point.
    """
    try:
        results = service.find_nearby(
            category_code=category,
            lat=lat,
            lon=lon,
            radius_m=radius_m,
            limit=limit,
        )
    except CoordinateValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors) from e

    return [NearbyFacilityRead.from_domain(r) for r in results]
