from fastapi import APIRouter, Depends

from app.api.v1.dependencies import get_category_service
from app.schemas.category import CategoryRead
from app.services.category_service import CategoryService

router = APIRouter(tags=["Categories"])


@router.get("/categories", response_model=list[CategoryRead])
def list_categories(
    service: CategoryService = Depends(get_category_service),  # noqa: B008
) -> list[CategoryRead]:
    return [CategoryRead(id=c.id, code=c.code, label=c.label) for c in service.list_active()]
