"""Feature engineering steps from the notebook's "Feature Engineering" section."""

import numpy as np
import pandas as pd

from kc_housing.config import (
    EARTH_RADIUS_KM,
    WEALTH_CENTER_COS_LAT,
    WEALTH_CENTER_LAT,
    WEALTH_CENTER_LONG,
)

KM_PER_DEGREE = 2 * np.pi * EARTH_RADIUS_KM / 360


def dist(long, lat, ref_long, ref_lat):
    """Approximate distance in km between a location and a reference location.

    Works on scalars and on (broadcastable) NumPy arrays. Same formula as the notebook.
    """
    delta_long_corr = (long - ref_long) * np.cos(np.radians(ref_lat))
    delta_lat = lat - ref_lat
    return np.sqrt(delta_long_corr**2 + delta_lat**2) * KM_PER_DEGREE


def add_sqft_price(df: pd.DataFrame) -> pd.DataFrame:
    """Price per square foot of living + lot area (used for analysis, not as a feature)."""
    df = df.copy()
    df["sqft_price"] = (df["price"] / (df["sqft_living"] + df["sqft_lot"])).round(2)
    return df


def add_center_distance(df: pd.DataFrame) -> pd.DataFrame:
    """Add ``delta_lat``, ``delta_long`` and ``center_distance`` (km to the wealth center)."""
    df = df.copy()
    df["delta_lat"] = np.absolute(WEALTH_CENTER_LAT - df["lat"])
    df["delta_long"] = np.absolute(WEALTH_CENTER_LONG - df["long"])
    df["center_distance"] = (
        np.sqrt(
            (df["delta_long"] * np.cos(np.radians(WEALTH_CENTER_COS_LAT))) ** 2
            + df["delta_lat"] ** 2
        )
        * KM_PER_DEGREE
    )
    return df


def waterfront_reference(df: pd.DataFrame) -> pd.DataFrame:
    """Coordinates of all waterfront houses, used as reference points for water distance."""
    return df.loc[df["waterfront"] == 1, ["long", "lat"]].reset_index(drop=True)


def add_water_distance(
    df: pd.DataFrame, reference: pd.DataFrame | None = None
) -> pd.DataFrame:
    """Add ``water_distance``: km to the nearest waterfront house.

    ``reference`` holds the waterfront coordinates (``long``, ``lat``). By default they
    are taken from ``df`` itself, as in the notebook. For new/unseen data, pass the
    reference built from the training data so predictions do not depend on the batch.

    The notebook used a nested Python loop (~3 million ``dist`` calls); NumPy
    broadcasting computes the same (n_houses x n_waterfront) matrix in one go.
    """
    if reference is None:
        reference = waterfront_reference(df)
    if reference.empty:
        raise ValueError("No waterfront houses available to compute water_distance.")

    df = df.copy()
    distances = dist(
        df["long"].to_numpy()[:, None],
        df["lat"].to_numpy()[:, None],
        reference["long"].to_numpy()[None, :],
        reference["lat"].to_numpy()[None, :],
    )
    df["water_distance"] = distances.min(axis=1)
    return df


def engineer_features(
    df: pd.DataFrame, water_reference: pd.DataFrame | None = None
) -> pd.DataFrame:
    """Run all feature engineering steps in the same order as the notebook."""
    return (
        df.pipe(add_sqft_price)
        .pipe(add_center_distance)
        .pipe(add_water_distance, reference=water_reference)
    )
