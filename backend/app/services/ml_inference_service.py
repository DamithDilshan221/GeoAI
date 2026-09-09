from sqlalchemy.orm import Session

from app.domain.exceptions import FacilityNotFoundError
from app.domain.ml_inference.provider import PredictionContext, PredictionResult
from app.domain.ml_inference.provider_factory import get_active_provider
from app.repositories.facility_repository import FacilityRepository
from app.repositories.usage_record_repository import UsageRecordRepository


class MLInferenceService:
    def __init__(
        self, session: Session, usage_repo: UsageRecordRepository, facility_repo: FacilityRepository
    ):
        self._session = session
        self._usage_repo = usage_repo
        self._facility_repo = facility_repo

    def predict_usage(
        self, *, facility_id: int, day_of_week: int, hour: int,
        recent_usage: float | None = None,
    ) -> PredictionResult:
        """
        1. facility = facility_repo.get_by_id(facility_id). If None,
           raise FacilityNotFoundError (reused from Phase 5B if it
           exists — see resolved decision #8).
        2. Validate day_of_week in [0,6], hour in [0,23] — raise a
           clear ValueError if not (the route maps this to 422).
        3. context = PredictionContext(...)
        4. provider = get_active_provider(...)
        5. return provider.predict(context)
        """
        facility = self._facility_repo.get_by_id(facility_id)
        if facility is None:
            raise FacilityNotFoundError(f"Facility {facility_id} not found")

        if not (0 <= day_of_week <= 6):
            raise ValueError(f"day_of_week must be between 0 and 6, got {day_of_week}")

        if not (0 <= hour <= 23):
            raise ValueError(f"hour must be between 0 and 23, got {hour}")

        context = PredictionContext(
            facility_id=facility.id,
            category_id=facility.category_id,
            capacity=facility.capacity,
            day_of_week=day_of_week,
            hour=hour,
            recent_usage=recent_usage
        )

        provider = get_active_provider(self._session, self._usage_repo, self._facility_repo)
        return provider.predict(context)
