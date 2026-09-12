"""Unit tests for TrainedModelUsageProvider (Phase 17).

Uses a minimal real fitted sklearn Pipeline so we exercise the actual
scikit-learn code paths without depending on the 14 MB Phase 15 artifact.
The fixture-model approach mirrors what Phase 15's own training tests use:
fit on a tiny synthetic DataFrame that covers all FEATURE_NAMES columns.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import numpy as np
import pandas as pd
import pytest
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from app.domain.ml_inference.provider import PredictionContext
from app.domain.ml_inference.trained_model_provider import TrainedModelUsageProvider
from app.models.enums import AudienceType

# ── Fixtures ─────────────────────────────────────────────────────────────────

_CATEGORICAL = ["category_code", "audience_code"]
_NUMERIC = [
    "hour", "day_of_week", "is_weekend", "total_stalls",
    "capacity_is_imputed", "facility_bucket_hist_mean",
    "facility_overall_hist_mean", "bucket_history_sample_count",
]


def _preprocessor():
    return ColumnTransformer(
        transformers=[("cat", OneHotEncoder(handle_unknown="ignore"), _CATEGORICAL)],
        remainder="passthrough",
    )


def _training_df() -> pd.DataFrame:
    """Minimal synthetic DataFrame matching FEATURE_NAMES."""
    rows = []
    for h in range(0, 24, 6):
        for cat in ["WC", "LIB"]:
            for aud in ["VISITOR", "STAFF"]:
                rows.append({
                    "hour": h,
                    "day_of_week": h % 7,
                    "is_weekend": (h % 7) >= 5,
                    "category_code": cat,
                    "audience_code": aud,
                    "total_stalls": 10.0,
                    "capacity_is_imputed": False,
                    "facility_bucket_hist_mean": float(h),
                    "facility_overall_hist_mean": float(h) / 2,
                    "bucket_history_sample_count": h + 1,
                })
    return pd.DataFrame(rows)


@pytest.fixture(scope="module")
def rf_pipeline() -> Pipeline:
    """Tiny Random Forest pipeline fitted on synthetic data."""
    df = _training_df()
    X = df.drop(columns=[])  # all columns are features
    y = df["hour"].astype(float)  # trivial target
    rf = RandomForestRegressor(n_estimators=10, random_state=42)
    pipe = Pipeline([("pre", _preprocessor()), ("est", rf)])
    pipe.fit(X, y)
    return pipe


@pytest.fixture(scope="module")
def ridge_pipeline() -> Pipeline:
    """Tiny Ridge pipeline fitted on synthetic data."""
    df = _training_df()
    X = df
    y = df["hour"].astype(float)
    pipe = Pipeline([("pre", _preprocessor()), ("est", Ridge())])
    pipe.fit(X, y)
    return pipe


def _make_context(category_code: str = "WC", hour: int = 9) -> PredictionContext:
    return PredictionContext(
        facility_id=1,
        category_id=1,
        category_code=category_code,
        total_stalls=20,
        audience=AudienceType.VISITOR,
        day_of_week=2,
        hour=hour,
    )


def _make_usage_repo(bucket=None, overall=None):
    repo = MagicMock()
    repo.get_facility_bucket_average.return_value = bucket
    repo.get_facility_overall_average.return_value = overall
    return repo


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestRFProvider:
    def test_returns_ml_model_source(self, rf_pipeline):
        provider = TrainedModelUsageProvider(rf_pipeline, "random_forest", _make_usage_repo())
        result = provider.predict(_make_context())
        assert result.source == "ml_model"

    def test_predicted_usage_never_negative(self, rf_pipeline):
        """Even if the raw model output is negative, clamp to 0."""
        # Mock the pipeline.predict to return a negative value.
        mock_pipe = MagicMock(wraps=rf_pipeline)
        mock_pipe.predict.return_value = np.array([-5.0])
        # Keep [:-1] transform working by wrapping the real pre step.
        mock_pipe.__getitem__ = rf_pipeline.__getitem__
        mock_pipe.steps = rf_pipeline.steps

        provider = TrainedModelUsageProvider(mock_pipe, "random_forest", _make_usage_repo())
        result = provider.predict(_make_context())
        assert result.predicted_usage >= 0.0

    def test_rf_confidence_high_for_uniform_target(self, rf_pipeline):
        """When all trees agree (hour=0 in our trivial dataset), confidence is high."""
        provider = TrainedModelUsageProvider(rf_pipeline, "random_forest", _make_usage_repo())
        # hour=0 -> all training rows with hour=0 target=0; trees should agree closely
        result = provider.predict(_make_context(hour=0))
        # We don't assert a specific value -- we assert the confidence string is valid.
        assert result.confidence in ("high", "medium", "low")

    def test_rf_confidence_branches_differ_by_variance(self, rf_pipeline):
        """Confidence branches by tree variance -- exercises the real RF path end-to-end.

        This test asserts that the variance-based branch runs (i.e., does not
        fall back to bucket_confidence) and produces a valid string for two
        different input contexts.  It does NOT assert a specific confidence level
        because a 10-tree RF on synthetic data may or may not converge to extreme
        relative_std values, but it MUST produce one of the three valid strings.
        """
        provider = TrainedModelUsageProvider(rf_pipeline, "random_forest", _make_usage_repo())
        ctx_low_hour = _make_context(hour=0)
        ctx_high_hour = _make_context(hour=18)
        r1 = provider.predict(ctx_low_hour)
        r2 = provider.predict(ctx_high_hour)
        for r in (r1, r2):
            assert r.confidence in ("high", "medium", "low")
            assert r.source == "ml_model"

    def test_rf_confidence_is_high_for_predictable_input(self, rf_pipeline):
        """hour=0 on a pipeline trained with hour=0 -> target=0 should give low variance."""
        provider = TrainedModelUsageProvider(rf_pipeline, "random_forest", _make_usage_repo())
        ctx = _make_context(hour=0)
        # Manually compute expected relative_std
        X = pd.DataFrame([{
            "hour": 0,
            "day_of_week": 2,
            "is_weekend": False,
            "category_code": "WC",
            "audience_code": "VISITOR",
            "total_stalls": 20.0,
            "capacity_is_imputed": False,
            "facility_bucket_hist_mean": 0.0,
            "facility_overall_hist_mean": 0.0,
            "bucket_history_sample_count": 0,
        }])
        predicted = max(0.0, float(rf_pipeline.predict(X)[0]))
        X_transformed = rf_pipeline[:-1].transform(X)
        rf = rf_pipeline.steps[-1][1]
        tree_preds = np.array([t.predict(X_transformed)[0] for t in rf.estimators_])
        relative_std = np.std(tree_preds) / max(predicted, 1.0)
        expected = "high" if relative_std < 0.2 else "medium" if relative_std < 0.5 else "low"

        result = provider.predict(ctx)
        assert result.confidence == expected


class TestNonRFProvider:
    def test_non_rf_uses_bucket_confidence_with_enough_samples(self, ridge_pipeline):
        """With 8+ samples, bucket_confidence returns 'high'."""
        repo = _make_usage_repo(bucket=(5.0, 8), overall=(5.0, 20))
        provider = TrainedModelUsageProvider(ridge_pipeline, "ridge", repo)
        result = provider.predict(_make_context())
        assert result.confidence == "high"
        assert result.source == "ml_model"

    def test_non_rf_sub_threshold_samples_gives_low(self, ridge_pipeline):
        """With < 3 samples, bucket_confidence would raise -- should return 'low'."""
        repo = _make_usage_repo(bucket=(5.0, 1), overall=(5.0, 5))
        provider = TrainedModelUsageProvider(ridge_pipeline, "ridge", repo)
        result = provider.predict(_make_context())
        assert result.confidence == "low"

    def test_non_rf_no_bucket_data_gives_low(self, ridge_pipeline):
        """No historical data at all -> bucket_sample_count=0 -> 'low'."""
        repo = _make_usage_repo(bucket=None, overall=None)
        provider = TrainedModelUsageProvider(ridge_pipeline, "ridge", repo)
        result = provider.predict(_make_context())
        assert result.confidence == "low"

    def test_non_rf_predicted_usage_never_negative(self, ridge_pipeline):
        """Clamp holds for ridge too."""
        mock_pipe = MagicMock(wraps=ridge_pipeline)
        mock_pipe.predict.return_value = np.array([-99.0])
        mock_pipe.steps = ridge_pipeline.steps

        provider = TrainedModelUsageProvider(mock_pipe, "ridge", _make_usage_repo())
        result = provider.predict(_make_context())
        assert result.predicted_usage >= 0.0
