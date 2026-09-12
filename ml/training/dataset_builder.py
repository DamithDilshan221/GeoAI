"""Vectorized, leakage-safe feature building over a raw usage_records
DataFrame. Mirrors app.domain.ml_inference.feature_engineering's arithmetic
exactly (parity enforced by ml/training/tests/)."""
from __future__ import annotations

import pandas as pd

from app.domain.ml_inference.feature_engineering import FEATURE_NAMES


def build_training_frame(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.sort_values(["facility_id", "date"]).reset_index(drop=True)

    df["facility_bucket_hist_mean"] = (
        df.groupby(["facility_id", "day_of_week", "hour"], group_keys=False)["usage_count"]
        .apply(lambda s: s.shift(1).expanding().mean())
    )
    df["bucket_history_sample_count"] = (
        df.groupby(["facility_id", "day_of_week", "hour"], group_keys=False)["usage_count"]
        .apply(lambda s: s.shift(1).expanding().count())
    )
    df["facility_overall_hist_mean"] = (
        df.groupby("facility_id", group_keys=False)["usage_count"]
        .apply(lambda s: s.shift(1).expanding().mean())
    )

    # Cold-start rows (no prior history yet) -> 0, matching the heuristic's
    # own Tier-4 fallback shape.
    df[["facility_bucket_hist_mean", "facility_overall_hist_mean"]] = (
        df[["facility_bucket_hist_mean", "facility_overall_hist_mean"]].fillna(0.0)
    )
    df["bucket_history_sample_count"] = df["bucket_history_sample_count"].fillna(0).astype(int)

    df["is_weekend"] = df["day_of_week"] >= 5
    df["capacity_is_imputed"] = df["total_stalls"] <= 0
    df["total_stalls"] = df["total_stalls"].where(df["total_stalls"] > 0, 10.0).astype(float)

    keep_cols = ["facility_id", "date", *FEATURE_NAMES, "usage_count"]
    return df[keep_cols]
