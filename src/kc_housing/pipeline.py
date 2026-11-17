"""End-to-end preprocessing pipeline: load -> clean -> engineer features -> save.

Run from the project root with ``uv run kc-preprocess``.
"""

import argparse
from pathlib import Path

import pandas as pd

from kc_housing.config import PROCESSED_DATA_PATH, RAW_DATA_PATH
from kc_housing.data_cleaning import clean_data
from kc_housing.feature_engineering import engineer_features


def load_data(path: str | Path = RAW_DATA_PATH) -> pd.DataFrame:
    """Load the raw King County CSV."""
    return pd.read_csv(path)


def preprocess(
    df: pd.DataFrame, water_reference: pd.DataFrame | None = None
) -> pd.DataFrame:
    """Apply all cleaning and feature engineering steps to a raw DataFrame."""
    return engineer_features(clean_data(df), water_reference=water_reference)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Clean and feature-engineer the data.")
    parser.add_argument("--input", type=Path, default=RAW_DATA_PATH)
    parser.add_argument("--output", type=Path, default=PROCESSED_DATA_PATH)
    args = parser.parse_args(argv)

    df = preprocess(load_data(args.input))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False)
    print(f"Saved {df.shape[0]} rows x {df.shape[1]} columns to {args.output}")


if __name__ == "__main__":
    main()
