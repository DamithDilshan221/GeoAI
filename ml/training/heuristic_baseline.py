"""Pure-pandas port of HeuristicUsageProvider's tiered logic (spec §15.5),
for offline comparison ONLY. Parity with the live class is enforced by
ml/training/tests/test_heuristic_baseline.py -- if the two diverge, that
test fails. All aggregates use TRAIN-ONLY history."""
import pandas as pd


def predict_heuristic(train_df: pd.DataFrame, test_df: pd.DataFrame) -> pd.Series:
    def _tier(cols: list[str], min_samples: int) -> pd.Series:
        agg = train_df.groupby(cols)["usage_count"].agg(["mean", "count"]).reset_index()
        agg = agg[agg["count"] >= min_samples]
        return agg.set_index(cols)["mean"]

    tier1 = _tier(["facility_id", "day_of_week", "hour"], 3)
    tier2 = _tier(["category_code", "day_of_week", "hour"], 3)
    tier3 = _tier(["day_of_week", "hour"], 1)

    preds = []
    for _, row in test_df.iterrows():
        k1 = (row["facility_id"], row["day_of_week"], row["hour"])
        k2 = (row["category_code"], row["day_of_week"], row["hour"])
        k3 = (row["day_of_week"], row["hour"])
        if k1 in tier1.index:
            preds.append(tier1.loc[k1])
        elif k2 in tier2.index:
            preds.append(tier2.loc[k2])
        elif k3 in tier3.index:
            preds.append(tier3.loc[k3])
        else:
            preds.append(0.0)
    return pd.Series(preds, index=test_df.index)
