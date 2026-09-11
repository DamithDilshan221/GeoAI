"""Router for nearby spatial search endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.v1.dependencies import get_nearby_search_service
from app.api.v1.parsers import parse_audience
from app.domain.gis.exceptions import CoordinateValidationError
from app.domain.gis.nearby_search_service import NearbySearchService
from app.schemas.nearby_washroom import NearbyWashroomRead

router = APIRouter(tags=["Facilities"])


@router.get("/washrooms/nearby", response_model=list[NearbyWashroomRead])
def get_nearby_washrooms(
    lat: float = Query(...),
    lon: float = Query(...),
    category: str = Query(...),
    audience: str | None = Query(default=None),
    radius_m: int = Query(default=1000, ge=1, le=10000),
    limit: int = Query(default=25, ge=1, le=50),
    service: NearbySearchService = Depends(get_nearby_search_service),  # noqa: B008
) -> list[NearbyWashroomRead]:
    """Search for nearby facilities.

    Returns a flat array of OPEN, active facilities of the requested category,
    ordered by distance from the provided point.
    """
    parsed_audience = parse_audience(audience)
    try:
        results = service.find_nearby(
            category_code=category,
            audience=parsed_audience,
            lat=lat,
            lon=lon,
            radius_m=radius_m,
            limit=limit,
        )
    except CoordinateValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors) from e

    return [NearbyWashroomRead.from_domain(r) for r in results]
