from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.repositories.category_repository import CategoryRepository
from app.repositories.facility_repository import FacilityRepository
from app.services.category_service import CategoryService
from app.services.facility_service import FacilityService


def get_category_service(session: Session = Depends(get_db_session)) -> CategoryService:  # noqa: B008
    repo = CategoryRepository(session)
    return CategoryService(repo)


def get_facility_service(session: Session = Depends(get_db_session)) -> FacilityService:  # noqa: B008
    facility_repo = FacilityRepository(session)
    category_repo = CategoryRepository(session)
    return FacilityService(facility_repo, category_repo)
