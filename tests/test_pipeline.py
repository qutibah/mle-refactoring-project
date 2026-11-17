import numpy as np
import pandas as pd
import pytest

from kc_housing.config import RAW_DATA_PATH
from kc_housing.data_cleaning import (
    add_last_known_change,
    clean_data,
    drop_implausible_bedrooms,
    fill_missing_with_zero,
    recalculate_basement,
)
from kc_housing.feature_engineering import add_water_distance, dist, engineer_features
from kc_housing.modeling import split_features_target
from kc_housing.pipeline import load_data, preprocess


@pytest.fixture
def raw_sample() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "id": [1, 2, 3],
            "price": [300000.0, 500000.0, 640000.0],
            "bedrooms": [3, 33, 4],
            "sqft_living": [1500, 1620, 2000],
            "sqft_lot": [5000, 6000, 7000],
            "sqft_above": [1000, 1620, 2000],
            "sqft_basement": ["500.0", "?", "0.0"],
            "view": [np.nan, 0.0, 2.0],
            "waterfront": [0.0, np.nan, 1.0],
            "yr_built": [1950, 1947, 1990],
            "yr_renovated": [np.nan, 0.0, 2005.0],
            "lat": [47.5, 47.6, 47.7],
            "long": [-122.2, -122.3, -122.25],
        }
    )


def test_drop_implausible_bedrooms(raw_sample):
    assert drop_implausible_bedrooms(raw_sample)["bedrooms"].max() == 4


def test_recalculate_basement(raw_sample):
    result = recalculate_basement(raw_sample)
    assert result["sqft_basement"].tolist() == [500, 0, 0]


def test_fill_missing_with_zero(raw_sample):
    result = fill_missing_with_zero(raw_sample)
    assert result[["view", "waterfront"]].isna().sum().sum() == 0


def test_add_last_known_change(raw_sample):
    result = add_last_known_change(raw_sample)
    assert result["last_known_change"].tolist() == [1950, 1947, 2005]
    assert "yr_built" not in result and "yr_renovated" not in result


def test_functions_do_not_mutate_input(raw_sample):
    before = raw_sample.copy()
    engineer_features(clean_data(raw_sample))
    pd.testing.assert_frame_equal(raw_sample, before)


def test_dist_is_zero_for_same_point():
    assert dist(-122.2, 47.5, -122.2, 47.5) == 0


def test_water_distance_zero_for_waterfront_house(raw_sample):
    result = add_water_distance(clean_data(raw_sample))
    assert result.loc[result["waterfront"] == 1, "water_distance"].eq(0).all()


def test_split_features_target_has_no_leakage(raw_sample):
    X, y = split_features_target(preprocess(raw_sample))
    assert not {"price", "sqft_price", "id", "date"} & set(X.columns)
    assert y.name == "price"


# --- Equivalence with the original notebook code -------------------------------


def notebook_reference(kc_data: pd.DataFrame, n_water_rows: int) -> pd.DataFrame:
    """The notebook's original cleaning + feature engineering code, copied verbatim.

    Water distance is only computed for the first ``n_water_rows`` rows because the
    original nested loop is very slow.
    """
    kc_data = kc_data.copy()
    kc_data.drop(15856, axis=0, inplace=True)
    kc_data["sqft_basement"] = kc_data["sqft_living"] - kc_data["sqft_above"]
    kc_data["view"] = kc_data["view"].fillna(0)
    kc_data["waterfront"] = kc_data["waterfront"].fillna(0)
    last_known_change = []
    for idx, yr_re in kc_data["yr_renovated"].items():
        if str(yr_re) == "nan" or yr_re == 0.0:
            last_known_change.append(kc_data["yr_built"][idx])
        else:
            last_known_change.append(int(yr_re))
    kc_data["last_known_change"] = last_known_change
    kc_data.drop("yr_renovated", axis=1, inplace=True)
    kc_data.drop("yr_built", axis=1, inplace=True)
    kc_data["sqft_price"] = (
        kc_data.price / (kc_data.sqft_living + kc_data.sqft_lot)
    ).round(2)
    kc_data["delta_lat"] = np.absolute(47.62774 - kc_data["lat"])
    kc_data["delta_long"] = np.absolute(-122.24194 - kc_data["long"])
    kc_data["center_distance"] = (
        (
            (kc_data["delta_long"] * np.cos(np.radians(47.6219))) ** 2
            + kc_data["delta_lat"] ** 2
        )
        ** (1 / 2)
        * 2
        * np.pi
        * 6378
        / 360
    )
    water_list = kc_data.query("waterfront == 1")
    water_distance = []
    for idx in kc_data.index[:n_water_rows]:
        ref_list = []
        for x, y in zip(list(water_list["long"]), list(water_list["lat"])):
            ref_list.append(dist(kc_data["long"][idx], kc_data["lat"][idx], x, y))
        water_distance.append(min(ref_list))
    kc_data = kc_data.loc[kc_data.index[:n_water_rows]].copy()
    kc_data["water_distance"] = water_distance
    return kc_data


@pytest.mark.skipif(not RAW_DATA_PATH.exists(), reason="dataset not available")
def test_pipeline_matches_notebook():
    raw = load_data()
    n = 100
    expected = notebook_reference(raw, n_water_rows=n)
    result = preprocess(raw).loc[expected.index]

    assert preprocess(raw).shape == (21596, 25)
    pd.testing.assert_frame_equal(
        result[expected.columns], expected, check_dtype=False
    )
