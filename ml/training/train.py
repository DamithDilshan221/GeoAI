"""Run with: python -m training.train  (from ml/, ml/requirements.txt
installed). Persists NOTHING -- prints a comparison report and exits 0."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit

from training.data_extraction import data_source_composition, extract_usage_dataframe
from training.dataset_builder import build_training_frame
from training.heuristic_baseline import predict_heuristic
from training.models import get_candidates

TEST_DATE_FRACTION = 0.20


def time_based_split(df):
    dates = sorted(df["date"].unique())
    n_test = max(1, round(len(dates) * TEST_DATE_FRACTION))
    test_dates = set(dates[-n_test:])
    mask = df["date"].isin(test_dates)
    return df[~mask].reset_index(drop=True), df[mask].reset_index(drop=True)


def main() -> None:
    raw = extract_usage_dataframe()
    print(f"Extracted {len(raw)} raw rows.")
    print(f"data_source composition: {data_source_composition(raw)}")

    frame = build_training_frame(raw)
    train_df, test_df = time_based_split(frame)
    print(f"Train: {len(train_df)} rows / {train_df['date'].nunique()} dates.")
    print(f"Test:  {len(test_df)} rows / {test_df['date'].nunique()} dates.")

    feature_cols = [c for c in frame.columns if c not in ("facility_id", "date", "usage_count")]
    X_train, y_train = train_df[feature_cols], train_df["usage_count"]
    X_test, y_test = test_df[feature_cols], test_df["usage_count"]

    heuristic_preds = predict_heuristic(train_df, test_df)
    heuristic_mae = mean_absolute_error(y_test, heuristic_preds)
    heuristic_r2 = r2_score(y_test, heuristic_preds)
    print(f"\nHeuristic baseline -- MAE: {heuristic_mae:.3f}  R2: {heuristic_r2:.3f}")

    results = []
    for c in get_candidates():
        search = GridSearchCV(c.pipeline, c.param_grid, cv=TimeSeriesSplit(5),
                               scoring="neg_mean_absolute_error", n_jobs=-1)
        search.fit(X_train, y_train)
        preds = search.predict(X_test)
        mae = mean_absolute_error(y_test, preds)
        r2 = r2_score(y_test, preds)
        results.append({"candidate": c.name, "mae": mae, "r2": r2,
                         "beats_heuristic": mae < heuristic_mae, "best_params": search.best_params_})
        print(f"\n{c.name} -- MAE: {mae:.3f}  R2: {r2:.3f}  "
              f"beats_heuristic: {mae < heuristic_mae}  best_params: {search.best_params_}")

    winner = min(results, key=lambda r: r["mae"])
    print(f"\nBest candidate by MAE: {winner['candidate']} (MAE={winner['mae']:.3f})")
    if winner["mae"] < heuristic_mae:
        print("=> Beats the heuristic -- eligible for Phase 16 promotion.")
    else:
        print("=> No candidate beat the heuristic. Per spec §15.5 the system continues "
              "running on the heuristic permanently -- a fully anticipated outcome.")


if __name__ == "__main__":
    main()
