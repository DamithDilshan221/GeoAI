from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.domain.gis.nearby_search_service import NearbySearchService
from app.repositories.category_repository import CategoryRepository
from app.repositories.facility_repository import FacilityRepository
from app.repositories.gis_repository import GISRepository


def get_category_service(session: Session = Depends(get_db_session)) -> "CategoryService":  # noqa: B008, F821
    from app.services.category_service import CategoryService

    repo = CategoryRepository(session)
    return CategoryService(repo)


def get_facility_service(session: Session = Depends(get_db_session)) -> "FacilityService":  # noqa: B008, F821
    from app.services.facility_service import FacilityService

    facility_repo = FacilityRepository(session)
    category_repo = CategoryRepository(session)
    return FacilityService(facility_repo, category_repo)


def get_gis_repository(session: Session = Depends(get_db_session)) -> GISRepository:  # noqa: B008
    return GISRepository(session)


def get_nearby_search_service(
    gis_repo: GISRepository = Depends(get_gis_repository),  # noqa: B008
    session: Session = Depends(get_db_session),  # noqa: B008
) -> NearbySearchService:
    category_repo = CategoryRepository(session)
    return NearbySearchService(gis_repo, category_repo)


def get_pedestrian_routing_service(
    session: Session = Depends(get_db_session),  # noqa: B008
) -> "PedestrianRoutingService":  # noqa: F821
    from app.core.config import get_settings
    from app.domain.routing.pedestrian_routing_service import PedestrianRoutingService

    settings = get_settings()
    facility_repo = FacilityRepository(session)
    return PedestrianRoutingService(
        facility_repo=facility_repo,
        osrm_base_url=settings.OSRM_BASE_URL,
        walking_speed_mps=settings.PEDESTRIAN_WALKING_SPEED_MPS,
    )


def get_ml_inference_service(
    session: Session = Depends(get_db_session),  # noqa: B008
) -> "MLInferenceService":  # noqa: F821
    from app.repositories.ml_model_version_repository import MLModelVersionRepository
    from app.repositories.usage_record_repository import UsageRecordRepository
    from app.services.ml_inference_service import MLInferenceService

    usage_repo = UsageRecordRepository(session)
    facility_repo = FacilityRepository(session)
    category_repo = CategoryRepository(session)
    model_version_repo = MLModelVersionRepository(session)
    return MLInferenceService(session, usage_repo, facility_repo, category_repo, model_version_repo)


def get_recommendation_service(
    session: Session = Depends(get_db_session),  # noqa: B008
    nearby_search: NearbySearchService = Depends(get_nearby_search_service),  # noqa: B008
    routing_service: "PedestrianRoutingService" = Depends(get_pedestrian_routing_service),  # noqa: B008, F821
    ml_service: "MLInferenceService" = Depends(get_ml_inference_service),  # noqa: B008, F821
) -> "RecommendationService":  # noqa: F821
    from app.repositories.ml_model_version_repository import MLModelVersionRepository
    from app.repositories.recommendation_log_repository import RecommendationLogRepository
    from app.services.recommendation_service import RecommendationService

    facility_repo = FacilityRepository(session)
    log_repo = RecommendationLogRepository(session)
    model_version_repo = MLModelVersionRepository(session)
    return RecommendationService(
        nearby_search=nearby_search,
        routing_service=routing_service,
        ml_service=ml_service,
        facility_repo=facility_repo,
        log_repo=log_repo,
        model_version_repo=model_version_repo,
    )
