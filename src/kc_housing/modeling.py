"""Stretch goal: the notebook's final model (polynomial ElasticNet + grid search).

Run from the project root with ``uv run kc-train``.
"""

import argparse
from pathlib import Path

import pandas as pd
import skops.io as sio
from sklearn.compose import TransformedTargetRegressor
from sklearn.linear_model import ElasticNet
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler

from kc_housing.config import (
    MODEL_PATH,
    NON_FEATURE_COLUMNS,
    RANDOM_STATE,
    RAW_DATA_PATH,
    TARGET,
    TEST_SIZE,
)
from kc_housing.pipeline import load_data, preprocess

PARAM_GRID = {
    "model__regressor__alpha": [0.01, 0.1, 1],
    "model__regressor__l1_ratio": [0.2, 0.5, 0.8],
}


def split_features_target(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Drop leakage/helper columns and ``id``; return features ``X`` and target ``y``."""
    features = [c for c in df.columns if c not in NON_FEATURE_COLUMNS and c != "id"]
    return df[features], df[TARGET]


def build_model() -> Pipeline:
    """Polynomial features -> scaling -> ElasticNet with a standardised target."""
    return Pipeline(
        [
            ("polynomial", PolynomialFeatures(2, include_bias=False)),
            ("scaler", StandardScaler()),
            (
                "model",
                TransformedTargetRegressor(
                    regressor=ElasticNet(max_iter=5000, tol=1e-4, precompute=True),
                    transformer=StandardScaler(),
                ),
            ),
        ]
    )


def train(X_train: pd.DataFrame, y_train: pd.Series, cv: int = 5) -> GridSearchCV:
    """Tune the ElasticNet pipeline with grid search and cross-validation."""
    search = GridSearchCV(
        build_model(), PARAM_GRID, cv=cv, scoring="r2", n_jobs=1, error_score="raise"
    )
    return search.fit(X_train, y_train)


def save_model(model, path: str | Path = MODEL_PATH) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f_out:
        sio.dump(model, f_out)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Train and save the price model.")
    parser.add_argument("--input", type=Path, default=RAW_DATA_PATH)
    parser.add_argument("--model-path", type=Path, default=MODEL_PATH)
    args = parser.parse_args(argv)

    X, y = split_features_target(preprocess(load_data(args.input)))
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )
    search = train(X_train, y_train)
    model = search.best_estimator_
    print("Best parameters:", search.best_params_)
    print("Test R^2:", round(model.score(X_test, y_test), 3))
    save_model(model, args.model_path)
    print(f"Model saved to {args.model_path}")


if __name__ == "__main__":
    main()
