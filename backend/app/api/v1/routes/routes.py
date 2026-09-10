"""API routes for pedestrian routing."""

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.v1.dependencies import get_pedestrian_routing_service
from app.domain.gis.exceptions import CoordinateValidationError
from app.domain.gis.pedestrian_routing_service import PedestrianRoutingService
from app.schemas.route import RouteResultRead

router = APIRouter(prefix="/routes", tags=["Routing"])


@router.get("", response_model=RouteResultRead)
def get_route(
    lat: float = Query(..., description="Origin latitude (-90 to 90)."),
    lon: float = Query(..., description="Origin longitude (-180 to 180)."),
    facility_id: int = Query(..., description="Target facility ID."),
    accessible_only: bool = Query(False, description="Exclude non-accessible paths like stairs."),
    routing_service: PedestrianRoutingService = Depends(get_pedestrian_routing_service),  # noqa: B008
) -> RouteResultRead:
    """Calculate the shortest walking path to a facility.

    Performs dynamic snapping and generates a path array over the pgRouting network.
    Falls back to a straight-line estimation if no network path is available.
    """
    try:
        result = routing_service.get_route(
            origin_lat=lat,
            origin_lon=lon,
            facility_id=facility_id,
            accessible_only=accessible_only,
        )
    except CoordinateValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors) from e

    if not result:
        raise HTTPException(status_code=404, detail="Facility not found or inactive")

    return RouteResultRead.from_domain(result)
