import pytest

from app.domain.ml_inference.feature_engineering import (
    FEATURE_NAMES,
    HistoricalAggregates,
    build_feature_dict,
    is_weekend,
)


def test_build_feature_dict_keys_match():
    hist = HistoricalAggregates(
        facility_bucket_hist_mean=5.0,
        facility_overall_hist_mean=6.0,
        bucket_history_sample_count=2,
    )
    features = build_feature_dict(
        hour=10,
        day_of_week=0,
        category_code="WC",
        audience_code="ALL",
        total_stalls=5,
        historical=hist,
    )
    assert set(features.keys()) == set(FEATURE_NAMES)
    assert "facility_id" not in features

@pytest.mark.parametrize("day, expected", [
    (0, False), # Monday
    (4, False), # Friday
    (5, True),  # Saturday
    (6, True),  # Sunday
])
def test_is_weekend(day, expected):
    assert is_weekend(day) == expected

def test_total_stalls_imputation():
    hist = HistoricalAggregates(
        facility_bucket_hist_mean=0.0,
        facility_overall_hist_mean=0.0,
        bucket_history_sample_count=0,
    )

    # 0 stalls -> imputes to 10.0
    f1 = build_feature_dict(
        hour=10, day_of_week=0, category_code="WC", audience_code="ALL",
        total_stalls=0, historical=hist
    )
    assert f1["total_stalls"] == 10.0
    assert f1["capacity_is_imputed"] is True

    # 15 stalls -> no imputation
    f2 = build_feature_dict(
        hour=10, day_of_week=0, category_code="WC", audience_code="ALL",
        total_stalls=15, historical=hist
    )
    assert f2["total_stalls"] == 15.0
    assert f2["capacity_is_imputed"] is False

def test_facility_id_never_present():
    hist = HistoricalAggregates(
        facility_bucket_hist_mean=5.0,
        facility_overall_hist_mean=6.0,
        bucket_history_sample_count=2,
    )
    features = build_feature_dict(
        hour=10,
        day_of_week=0,
        category_code="WC",
        audience_code="ALL",
        total_stalls=5,
        historical=hist,
    )
    assert "facility_id" not in features
