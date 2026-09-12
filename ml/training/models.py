"""Candidate models + hyperparameter grids (spec §15.6). category_code/
audience_code are one-hot encoded (resolved decision #7)."""
from dataclasses import dataclass

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

_CATEGORICAL = ["category_code", "audience_code"]


def _preprocessor() -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[("cat", OneHotEncoder(handle_unknown="ignore"), _CATEGORICAL)],
        remainder="passthrough",
    )


@dataclass(frozen=True)
class Candidate:
    name: str
    pipeline: Pipeline
    param_grid: dict


def get_candidates() -> list[Candidate]:
    return [
        Candidate(
            "ridge",
            Pipeline([("pre", _preprocessor()), ("est", Ridge())]),
            {"est__alpha": [0.1, 1.0, 10.0]},
        ),
        Candidate(
            "random_forest",
            Pipeline([("pre", _preprocessor()), ("est", RandomForestRegressor(random_state=42))]),
            {"est__n_estimators": [100, 300], "est__max_depth": [10, 20, None], "est__min_samples_leaf": [1, 3]},
        ),
        Candidate(
            "hist_gradient_boosting",
            Pipeline([("pre", _preprocessor()), ("est", HistGradientBoostingRegressor(random_state=42))]),
            {"est__max_iter": [100, 300], "est__max_depth": [None, 10], "est__learning_rate": [0.05, 0.1]},
        ),
    ]
