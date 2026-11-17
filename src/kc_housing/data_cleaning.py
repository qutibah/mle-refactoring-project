"""Data cleaning steps from the notebook's "Data Preparation" section.

Every function takes a DataFrame and returns a *new* DataFrame (no ``inplace=True``),
so the steps can be chained with ``DataFrame.pipe`` and tested in isolation.
"""

import pandas as pd

from kc_housing.config import MAX_PLAUSIBLE_BEDROOMS


def drop_implausible_bedrooms(
    df: pd.DataFrame, max_bedrooms: int = MAX_PLAUSIBLE_BEDROOMS
) -> pd.DataFrame:
    """Remove rows with an implausible bedroom count (the 33-bedroom, 1,620 sqft house).

    The notebook dropped the hard-coded index 15856; filtering by value works on any data.
    """
    return df[df["bedrooms"] <= max_bedrooms].copy()


def recalculate_basement(df: pd.DataFrame) -> pd.DataFrame:
    """Rebuild ``sqft_basement`` as ``sqft_living - sqft_above`` (fixes the ``?`` entries)."""
    df = df.copy()
    df["sqft_basement"] = df["sqft_living"] - df["sqft_above"]
    return df


def fill_missing_with_zero(
    df: pd.DataFrame, columns: tuple[str, ...] = ("view", "waterfront")
) -> pd.DataFrame:
    """Fill missing ``view`` and ``waterfront`` with 0, their most frequent value."""
    df = df.copy()
    for column in columns:
        df[column] = df[column].fillna(0)
    return df


def add_last_known_change(df: pd.DataFrame) -> pd.DataFrame:
    """Combine ``yr_built`` and ``yr_renovated`` into ``last_known_change``.

    Uses the renovation year when there is one, otherwise the build year, then drops
    both source columns. Vectorised replacement of the notebook's row-by-row loop.
    """
    df = df.copy()
    renovated = df["yr_renovated"].fillna(0)
    df["last_known_change"] = (
        df["yr_built"].where(renovated == 0, renovated).astype("int64")
    )
    return df.drop(columns=["yr_renovated", "yr_built"])


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Run all cleaning steps in the same order as the notebook."""
    return (
        df.pipe(drop_implausible_bedrooms)
        .pipe(recalculate_basement)
        .pipe(fill_missing_with_zero)
        .pipe(add_last_known_change)
    )
