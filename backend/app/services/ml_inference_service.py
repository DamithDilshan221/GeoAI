"""ML inference service -- orchestrates provider selection and prediction.

Phase 17 changes:
  - `category_repo` added to resolve `category_code` from `category_id`.
  - `model_version_repo` added so `get_active_provider` can query the
    active row through the repository layer (needed for `artifact_path`).
  - Predict-time fallback: if the active provider raises, log it and fall back
    to a fresh `HeuristicUsageProvider` for this single call.
"""

from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app.domain.exceptions import FacilityNotFoundError
from app.domain.ml_inference.heuristic_provider import HeuristicUsageProvider
from app.domain.ml_inference.provider import PredictionContext, PredictionResult
from app.domain.ml_inference.provider_factory import get_active_provider
from app.repositories.category_repository import CategoryRepository
from app.repositories.facility_repository import FacilityRepository
from app.repositories.ml_model_version_repository import MLModelVersionRepository
from app.repositories.usage_record_repository import UsageRecordRepository

logger = logging.getLogger(__name__)


class MLInferenceService:
    def __init__(
        self,
        session: Session,
        usage_repo: UsageRecordRepository,
        facility_repo: FacilityRepository,
        category_repo: CategoryRepository | None = None,
        model_version_repo: MLModelVersionRepository | None = None,
    ) -> None:
        self._session = session
        self._usage_repo = usage_repo
        self._facility_repo = facility_repo
        # Defaults to new instances if not injected -- keeps backward compat
        # for any test that constructs MLInferenceService with only 3 args.
        self._category_repo = category_repo or CategoryRepository(session)
        self._model_version_repo = model_version_repo or MLModelVersionRepository(session)

    def predict_usage(
        self,
        *,
        facility_id: int,
        day_of_week: int,
        hour: int,
        recent_usage: float | None = None,
    ) -> PredictionResult:
        """Predict usage for *facility_id* at the given time bucket.

        Steps:
        1. Resolve facility; raise `FacilityNotFoundError` if absent.
        2. Validate day_of_week in [0,6] and hour in [0,23].
        3. Resolve `category_code` via `category_repo.get_by_id()`.
        4. Build `PredictionContext`.
        5. Get the active provider (fresh DB read each call).
        6. Call `provider.predict()`.  On any exception: log, fall back to
           a fresh `HeuristicUsageProvider` for this single call.
        """
        facility = self._facility_repo.get_by_id(facility_id)
        if facility is None:
            raise FacilityNotFoundError(f"Facility {facility_id} not found")

        if not (0 <= day_of_week <= 6):
            raise ValueError(f"day_of_week must be between 0 and 6, got {day_of_week}")

        if not (0 <= hour <= 23):
            raise ValueError(f"hour must be between 0 and 23, got {hour}")

        # Resolve category_code for the trained-model path.  If the category
        # row is missing (shouldn't happen in a consistent DB) we use "" so
        # the model receives a known-unknown category_code (OHE handle_unknown="ignore").
        category = self._category_repo.get_by_id(facility.category_id)
        category_code = category.code if category is not None else ""

        context = PredictionContext(
            facility_id=facility.id,
            category_id=facility.category_id,
            category_code=category_code,
            total_stalls=facility.total_stalls,
            audience=facility.audience,
            day_of_week=day_of_week,
            hour=hour,
            recent_usage=recent_usage,
        )

        provider = get_active_provider(
            self._session,
            self._usage_repo,
            self._facility_repo,
            self._model_version_repo,
        )

        try:
            return provider.predict(context)
        except Exception:
            logger.exception(
                "Prediction failed for facility %d using active provider; "
                "falling back to heuristic for this call.",
                facility_id,
            )
            fallback = HeuristicUsageProvider(self._usage_repo, self._facility_repo)
            return fallback.predict(context)
