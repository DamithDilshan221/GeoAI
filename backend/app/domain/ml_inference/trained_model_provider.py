"""TrainedModelUsageProvider -- Phase 17 ML inference integration.

Wraps a fitted sklearn Pipeline loaded by `model_loader.load_model()`.
Implements confidence estimation per algorithm (resolved decision #5).
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from app.domain.ml_inference.crowd_level import (
    bucket_confidence,
    derive_crowd_level,
    resolve_effective_capacity,
)
from app.domain.ml_inference.feature_engineering import (
    HistoricalAggregates,
    build_feature_dict,
)
from app.domain.ml_inference.provider import (
    PredictionContext,
    PredictionResult,
    UsagePredictionProvider,
)
from app.repositories.usage_record_repository import UsageRecordRepository

logger = logging.getLogger(__name__)


class TrainedModelUsageProvider(UsagePredictionProvider):
    """Usage prediction via a trained sklearn Pipeline.

    Loaded once per distinct model version (via `model_loader.load_model()`),
    never once per request.  Confidence estimation branches on `algorithm`:

    * `"random_forest"` -- per-tree variance on the same preprocessed input
      the ensemble used, giving a data-driven relative-std confidence signal.
    * anything else -- falls back to Phase 10's `bucket_confidence()` bucketing
      on the bucket sample count; sub-threshold counts become `"low"` rather
      than propagating `bucket_confidence`'s `ValueError`.
    """

    def __init__(
        self,
        pipeline: object,
        algorithm: str,
        usage_repo: UsageRecordRepository,
    ) -> None:
        self._pipeline = pipeline
        self._algorithm = algorithm
        self._usage_repo = usage_repo

    def predict(self, context: PredictionContext) -> PredictionResult:
        # ── 1. Fetch historical aggregates ─────────────────────────────────
        bucket = self._usage_repo.get_facility_bucket_average(
            facility_id=context.facility_id,
            day_of_week=context.day_of_week,
            hour=context.hour,
        )
        if bucket is not None:
            facility_bucket_hist_mean, bucket_history_sample_count = bucket[0], bucket[1]
        else:
            facility_bucket_hist_mean, bucket_history_sample_count = None, 0

        overall = self._usage_repo.get_facility_overall_average(context.facility_id)
        facility_overall_hist_mean = overall[0] if overall is not None else None

        # ── 2. Build feature vector (shared source of truth -- §15.8) ─────
        hist = HistoricalAggregates(
            facility_bucket_hist_mean=facility_bucket_hist_mean
            if facility_bucket_hist_mean is not None
            else 0.0,
            facility_overall_hist_mean=facility_overall_hist_mean
            if facility_overall_hist_mean is not None
            else 0.0,
            bucket_history_sample_count=bucket_history_sample_count,
        )
        feature_dict = build_feature_dict(
            hour=context.hour,
            day_of_week=context.day_of_week,
            category_code=context.category_code,
            audience_code=context.audience.value,
            total_stalls=context.total_stalls,
            historical=hist,
        )

        # ── 3. Run inference ───────────────────────────────────────────────
        X = pd.DataFrame([feature_dict])
        raw_prediction = float(self._pipeline.predict(X)[0])
        predicted_usage = max(0.0, raw_prediction)

        # ── 4. Confidence estimation (resolved decision #5) ───────────────
        confidence = self._estimate_confidence(
            X=X,
            predicted_usage=predicted_usage,
            bucket_history_sample_count=bucket_history_sample_count,
        )

        # ── 5. Crowd level ────────────────────────────────────────────────
        effective_capacity = resolve_effective_capacity(context.total_stalls)
        crowd_level = derive_crowd_level(predicted_usage, effective_capacity)

        return PredictionResult(
            predicted_usage=round(predicted_usage, 1),
            crowd_level=crowd_level,
            source="ml_model",
            confidence=confidence,
        )

    def _estimate_confidence(
        self,
        *,
        X: pd.DataFrame,
        predicted_usage: float,
        bucket_history_sample_count: int,
    ) -> str:
        """Branch on algorithm to produce a confidence string.

        Random Forest: use per-tree variance on the preprocessed input.
        Other algorithms: use Phase 10's bucket sample-count bucketing.
        Thresholds (relative_std < 0.2 -> high, < 0.5 -> medium, else low)
        are this phase's own reasoned defaults, not spec-mandated numbers.
        """
        if self._algorithm == "random_forest":
            try:
                # Transform with all steps *except* the final estimator.
                # Pipeline supports slice notation: pipeline[:-1] gives a
                # sub-Pipeline of all but the last step.
                X_transformed = self._pipeline[:-1].transform(X)
                rf = self._pipeline.steps[-1][1]  # the fitted RandomForestRegressor
                tree_preds = np.array(
                    [t.predict(X_transformed)[0] for t in rf.estimators_]
                )
                relative_std = np.std(tree_preds) / max(predicted_usage, 1.0)
                if relative_std < 0.2:
                    return "high"
                if relative_std < 0.5:
                    return "medium"
                return "low"
            except Exception:
                logger.exception(
                    "RF confidence estimation failed; falling back to bucket bucketing"
                )
                # Fall through to bucket-based confidence below.

        # Non-RF path (Ridge, HistGradientBoosting, or RF fallback above).
        try:
            return bucket_confidence(bucket_history_sample_count)
        except ValueError:
            # bucket_confidence raises when sample_count < 3; that IS "low" here.
            return "low"
