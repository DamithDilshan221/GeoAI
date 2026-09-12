import pandas as pd
from training.dataset_builder import build_training_frame

def test_leakage_prevention_expanding_window():
    # 3-row single-facility DataFrame where the third (latest) date has an extreme usage_count=9999
    # We want to assert the first row's facility_bucket_hist_mean == 0.0 (cold start)
    # and the second row's facility_bucket_hist_mean == 5.0 (only the first row's value, never the extreme future one)
    # with bucket_history_sample_count == 1.
    
    df = pd.DataFrame([
        {
            "facility_id": "f1",
            "date": pd.to_datetime("2023-10-01"),
            "day_of_week": 0,
            "hour": 10,
            "usage_count": 5,
            "category_code": "WC",
            "audience_code": "ALL",
            "total_stalls": 2,
        },
        {
            "facility_id": "f1",
            "date": pd.to_datetime("2023-10-08"),
            "day_of_week": 0, # same day of week
            "hour": 10,       # same hour
            "usage_count": 7,
            "category_code": "WC",
            "audience_code": "ALL",
            "total_stalls": 2,
        },
        {
            "facility_id": "f1",
            "date": pd.to_datetime("2023-10-15"),
            "day_of_week": 0,
            "hour": 10,
            "usage_count": 9999, # extreme future value
            "category_code": "WC",
            "audience_code": "ALL",
            "total_stalls": 2,
        },
    ])
    
    result = build_training_frame(df)
    
    # Ordered by date, so index 0 is first, 1 is second, 2 is third
    # row 0: prior history = none -> mean=0.0, count=0
    assert result.loc[0, "facility_bucket_hist_mean"] == 0.0
    assert result.loc[0, "bucket_history_sample_count"] == 0
    
    # row 1: prior history = [5] -> mean=5.0, count=1
    assert result.loc[1, "facility_bucket_hist_mean"] == 5.0
    assert result.loc[1, "bucket_history_sample_count"] == 1
    
    # row 2: prior history = [5, 7] -> mean=6.0, count=2
    assert result.loc[2, "facility_bucket_hist_mean"] == 6.0
    assert result.loc[2, "bucket_history_sample_count"] == 2
