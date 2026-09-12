"""Leakage-safe feature engineering for usage prediction (spec §15.8, §15.9).

Single source of truth for the ML feature vector, imported by:
  - the offline training pipeline (ml/training/dataset_builder.py)
  - the live TrainedModelUsageProvider (Phase 17, not yet built)

Zero pandas/sklearn/numpy dependency on purpose -- stays importable from the
live FastAPI process without pulling in the training-time stack.
"""

from __future__ import annotations

from dataclasses import dataclass

FEATURE_NAMES: tuple[str, ...] = (
    "hour",
    "day_of_week",
    "is_weekend",
    "category_code",
    "audience_code",
    "total_stalls",
    "capacity_is_imputed",
    "facility_bucket_hist_mean",
    "facility_overall_hist_mean",
    "bucket_history_sample_count",
)

_DEFAULT_TOTAL_STALLS = 10.0  # matches resolve_effective_capacity's hard default


@dataclass(frozen=True)
class HistoricalAggregates:
    """Strictly-prior-dates aggregates for one (facility, day_of_week, hour) row.

    Callers compute these using ONLY usage_records with date < as_of_date --
    this module never touches a database or a DataFrame itself.
    """

    facility_bucket_hist_mean: float
    facility_overall_hist_mean: float
    bucket_history_sample_count: int


def is_weekend(day_of_week: int) -> bool:
    """day_of_week convention: Python's date.weekday(), Monday=0, Sunday=6."""
    return day_of_week >= 5


def build_feature_dict(
    *,
    hour: int,
    day_of_week: int,
    category_code: str,
    audience_code: str,
    total_stalls: int,
    historical: HistoricalAggregates,
) -> dict[str, object]:
    """Build one feature row, matching FEATURE_NAMES exactly.

    facility_id is deliberately not a parameter -- see spec §15.8.
    total_stalls <= 0 is imputed to the shared hard default (10.0), mirroring
    resolve_effective_capacity's own fallback.
    """
    capacity_is_imputed = total_stalls <= 0
    effective_stalls = float(total_stalls) if total_stalls > 0 else _DEFAULT_TOTAL_STALLS

    feature_row: dict[str, object] = {
        "hour": hour,
        "day_of_week": day_of_week,
        "is_weekend": is_weekend(day_of_week),
        "category_code": category_code,
        "audience_code": audience_code,
        "total_stalls": effective_stalls,
        "capacity_is_imputed": capacity_is_imputed,
        "facility_bucket_hist_mean": historical.facility_bucket_hist_mean,
        "facility_overall_hist_mean": historical.facility_overall_hist_mean,
        "bucket_history_sample_count": historical.bucket_history_sample_count,
    }

    assert set(feature_row) == set(FEATURE_NAMES), (
        "build_feature_dict output must exactly match FEATURE_NAMES"
    )
    assert "facility_id" not in feature_row, "facility_id must never be a feature -- spec §15.8"

    return feature_row
