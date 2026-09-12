"""Extend Phase 15's train pipeline to persist the winning model + manifest.

Run with:
    python -m training.persist        (from ml/)

Produces (under ml/models/):
    <version>.joblib          — the fitted sklearn Pipeline for the winner
    <version>_manifest.json   — §15.11 manifest consumed by backend/app/scripts/promote_model.py

§15.11 manifest schema (all fields required by promote_model.py):
    version                                 str  — e.g. "ridge-v1-20260912T134000Z"
    algorithm                               str  — candidate name
    trained_at                              str  — ISO-8601 UTC
    feature_list                            list[str]
    artifact_path                           str  — absolute path to .joblib
    evaluation_metrics.mae                  float
    evaluation_metrics.r2                   float
    evaluation_metrics.beats_heuristic      bool
    evaluation_metrics.heuristic_mae        float  — for the promote script's comparison report
    evaluation_metrics.heuristic_r2         float
    evaluation_metrics.test_dates           int    — number of distinct test dates
    evaluation_metrics.test_rows            int
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

import joblib
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit

from training.data_extraction import data_source_composition, extract_usage_dataframe
from training.dataset_builder import build_training_frame
from training.heuristic_baseline import predict_heuristic
from training.models import get_candidates
from app.domain.ml_inference.feature_engineering import FEATURE_NAMES

MODELS_DIR = Path(__file__).resolve().parents[1] / "models"
TEST_DATE_FRACTION = 0.20


def time_based_split(df):
    dates = sorted(df["date"].unique())
    n_test = max(1, round(len(dates) * TEST_DATE_FRACTION))
    test_dates = set(dates[-n_test:])
    mask = df["date"].isin(test_dates)
    return df[~mask].reset_index(drop=True), df[mask].reset_index(drop=True)


def main() -> None:
    MODELS_DIR.mkdir(exist_ok=True)

    # ── 1. Extract and split ────────────────────────────────────────────────
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

    # ── 2. Heuristic baseline (permanent competitor) ────────────────────────
    heuristic_preds = predict_heuristic(train_df, test_df)
    heuristic_mae = float(mean_absolute_error(y_test, heuristic_preds))
    heuristic_r2 = float(r2_score(y_test, heuristic_preds))
    print(f"\nHeuristic baseline -- MAE: {heuristic_mae:.4f}  R2: {heuristic_r2:.4f}")

    # ── 3. Train all candidates ─────────────────────────────────────────────
    results = []
    for c in get_candidates():
        search = GridSearchCV(
            c.pipeline, c.param_grid,
            cv=TimeSeriesSplit(5),
            scoring="neg_mean_absolute_error",
            n_jobs=-1,
        )
        search.fit(X_train, y_train)
        preds = search.predict(X_test)
        mae = float(mean_absolute_error(y_test, preds))
        r2 = float(r2_score(y_test, preds))
        results.append({
            "candidate": c.name,
            "pipeline": search.best_estimator_,
            "mae": mae,
            "r2": r2,
            "beats_heuristic": mae < heuristic_mae,
            "best_params": search.best_params_,
        })
        print(
            f"\n{c.name} -- MAE: {mae:.4f}  R2: {r2:.4f}  "
            f"beats_heuristic: {mae < heuristic_mae}  best_params: {search.best_params_}"
        )

    # ── 4. Pick winner (best MAE) ───────────────────────────────────────────
    winner = min(results, key=lambda r: r["mae"])
    print(f"\nBest candidate by MAE: {winner['candidate']} (MAE={winner['mae']:.4f})")

    # ── 5. Build version string ─────────────────────────────────────────────
    now_utc = datetime.now(timezone.utc)
    ts = now_utc.strftime("%Y%m%dT%H%M%SZ")
    version = f"{winner['candidate']}-v1-{ts}"

    # ── 6. Persist artifact ─────────────────────────────────────────────────
    artifact_path = MODELS_DIR / f"{version}.joblib"
    joblib.dump(winner["pipeline"], artifact_path)
    print(f"\nArtifact saved: {artifact_path}")

    # ── 7. Write manifest (§15.11) ──────────────────────────────────────────
    manifest = {
        "version": version,
        "algorithm": winner["candidate"],
        "trained_at": now_utc.isoformat(),
        "feature_list": list(feature_cols),
        "artifact_path": str(artifact_path),
        "evaluation_metrics": {
            "mae": winner["mae"],
            "r2": winner["r2"],
            "beats_heuristic": winner["beats_heuristic"],
            "heuristic_mae": heuristic_mae,
            "heuristic_r2": heuristic_r2,
            "test_dates": int(test_df["date"].nunique()),
            "test_rows": int(len(test_df)),
        },
    }

    manifest_path = MODELS_DIR / f"{version}_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"Manifest saved:  {manifest_path}")

    # ── 8. Promotion eligibility summary ───────────────────────────────────
    if winner["beats_heuristic"]:
        delta = heuristic_mae - winner["mae"]
        print(
            f"\n=> BEATS heuristic (MAE {winner['mae']:.4f} vs heuristic {heuristic_mae:.4f}, "
            f"delta {delta:.4f}) — eligible for Phase 16 promotion."
        )
    else:
        print(
            f"\n=> Does NOT beat heuristic (MAE {winner['mae']:.4f} vs heuristic {heuristic_mae:.4f}) "
            f"— per spec §15.5 the system continues on the heuristic."
        )

    print(f"\nManifest path for promote_model.py:\n  {manifest_path}")


if __name__ == "__main__":
    main()
