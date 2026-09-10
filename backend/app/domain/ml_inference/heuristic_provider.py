from app.domain.ml_inference.crowd_level import (
    bucket_confidence,
    derive_crowd_level,
    resolve_effective_capacity,
)
from app.domain.ml_inference.provider import (
    PredictionContext,
    PredictionResult,
    UsagePredictionProvider,
)
from app.repositories.facility_repository import FacilityRepository
from app.repositories.usage_record_repository import UsageRecordRepository


class HeuristicUsageProvider(UsagePredictionProvider):
    def __init__(self, usage_repo: UsageRecordRepository, facility_repo: FacilityRepository):
        self._usage_repo = usage_repo
        self._facility_repo = facility_repo

    def predict(self, context: PredictionContext) -> PredictionResult:
        """
        1. Tier 1: get_facility_bucket_average(...). If result exists
           and sample_count >= 3: predicted_usage = mean,
           confidence = bucket_confidence(sample_count). Otherwise
           continue to Tier 2.
        2. Tier 2: get_category_bucket_average(...). If result exists
           and sample_count >= 3: predicted_usage = mean,
           confidence = "low". Otherwise continue to Tier 3.
        3. Tier 3: get_global_bucket_average(...). If result exists:
           predicted_usage = mean, confidence = "low". Otherwise
           Tier 4: predicted_usage = 0, confidence = "low".
        4. Resolve effective_capacity: context.capacity if set, else
           facility_repo.get_category_median_capacity(context.category_id),
           else a hard-coded default (10).
        5. crowd_level = derive_crowd_level(predicted_usage, effective_capacity)
        6. Return PredictionResult(predicted_usage=round(predicted_usage, 1),
           crowd_level=crowd_level, source="heuristic", confidence=confidence)
        """
        predicted_usage = 0.0
        confidence = "low"
        resolved = False

        # Tier 1
        tier1 = self._usage_repo.get_facility_bucket_average(
            facility_id=context.facility_id, day_of_week=context.day_of_week, hour=context.hour
        )
        if tier1 is not None and tier1[1] >= 3:
            predicted_usage = tier1[0]
            confidence = bucket_confidence(tier1[1])
            resolved = True

        # Tier 2
        if not resolved:
            tier2 = self._usage_repo.get_category_bucket_average(
                category_id=context.category_id, day_of_week=context.day_of_week, hour=context.hour
            )
            if tier2 is not None and tier2[1] >= 3:
                predicted_usage = tier2[0]
                confidence = "low"
                resolved = True

        # Tier 3
        if not resolved:
            tier3 = self._usage_repo.get_global_bucket_average(
                day_of_week=context.day_of_week, hour=context.hour
            )
            if tier3 is not None:
                predicted_usage = tier3[0]
                confidence = "low"
                resolved = True

        # Tier 4 (fallback if still not resolved)
        if not resolved:
            predicted_usage = 0.0
            confidence = "low"
            # Deliberate safe default for an otherwise-impossible-in-normal-operation state.

        # Resolve effective_capacity via shared function (Phase 11 extraction)
        median_cap = self._facility_repo.get_category_median_capacity(context.category_id)
        effective_capacity = resolve_effective_capacity(
            capacity=context.capacity,
            category_median=median_cap,
        )

        crowd_level = derive_crowd_level(predicted_usage, effective_capacity)

        return PredictionResult(
            predicted_usage=round(predicted_usage, 1),
            crowd_level=crowd_level,
            source="heuristic",
            confidence=confidence,
        )
