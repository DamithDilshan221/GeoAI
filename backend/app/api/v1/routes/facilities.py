from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.v1.dependencies import get_facility_service
from app.models.enums import FacilityStatus
from app.schemas.facility import FacilityListResponse, FacilityRead
from app.services.facility_service import FacilityService

router = APIRouter(tags=["Facilities"])


@router.get("/facilities", response_model=FacilityListResponse)
def list_facilities(
    category: str | None = None,
    status: FacilityStatus | None = None,
    limit: int = Query(default=25, ge=1, le=50),  # noqa: B008
    offset: int = Query(default=0, ge=0),  # noqa: B008
    service: FacilityService = Depends(get_facility_service),  # noqa: B008
) -> FacilityListResponse:
    items, total = service.list(
        category_code=category,
        status=status,
        limit=limit,
        offset=offset,
    )
    return FacilityListResponse(
        items=[FacilityRead.from_domain(i) for i in items],
        limit=limit,
        offset=offset,
        total=total,
    )


@router.get("/facilities/{facility_id}", response_model=FacilityRead)
def get_facility(
    facility_id: int,
    service: FacilityService = Depends(get_facility_service),  # noqa: B008
) -> FacilityRead:
    result = service.get_by_id(facility_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Facility {facility_id} not found")
    return FacilityRead.from_domain(result)
