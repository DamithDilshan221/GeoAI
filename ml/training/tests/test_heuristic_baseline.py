import pandas as pd
from training.heuristic_baseline import predict_heuristic

def test_predict_heuristic_tier1_medium():
    # a 3-row train set with usage_count 4, 6, 8 for the same facility/day_of_week/hour bucket
    # must predict 6.0 for a test row in that bucket
    train_df = pd.DataFrame([
        {"facility_id": "f1", "day_of_week": 2, "hour": 14, "usage_count": 4, "category_code": "WC"},
        {"facility_id": "f1", "day_of_week": 2, "hour": 14, "usage_count": 6, "category_code": "WC"},
        {"facility_id": "f1", "day_of_week": 2, "hour": 14, "usage_count": 8, "category_code": "WC"},
    ])
    
    test_df = pd.DataFrame([
        {"facility_id": "f1", "day_of_week": 2, "hour": 14, "category_code": "WC"}
    ])
    
    preds = predict_heuristic(train_df, test_df)
    
    assert len(preds) == 1
    assert preds.iloc[0] == 6.0

def test_predict_heuristic_tier4_fallback():
    # an empty train set must predict 0.0
    train_df = pd.DataFrame(columns=["facility_id", "day_of_week", "hour", "usage_count", "category_code"])
    
    test_df = pd.DataFrame([
        {"facility_id": "f1", "day_of_week": 2, "hour": 14, "category_code": "WC"}
    ])
    
    preds = predict_heuristic(train_df, test_df)
    
    assert len(preds) == 1
    assert preds.iloc[0] == 0.0
