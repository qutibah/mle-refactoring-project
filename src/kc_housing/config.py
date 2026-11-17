"""Constants shared across the pipeline (previously magic numbers in the notebook)."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_PATH = PROJECT_ROOT / "data" / "King_County_House_prices_dataset.csv"
PROCESSED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "kc_house_clean.csv"
MODEL_PATH = PROJECT_ROOT / "model" / "model.bin"

# Earth radius (km) used by the notebook's flat-earth distance approximation.
EARTH_RADIUS_KM = 6378

# "Center of wealth": Bill Gates' residence in Medina.
WEALTH_CENTER_LAT = 47.62774
WEALTH_CENTER_LONG = -122.24194
# Latitude used for the longitude correction of the center distance.
WEALTH_CENTER_COS_LAT = 47.6219

# Rows with more bedrooms than this are treated as data-entry errors (the 33-bedroom house).
MAX_PLAUSIBLE_BEDROOMS = 30

# Columns removed before modeling: target, target-derived (leakage) or helper columns.
NON_FEATURE_COLUMNS = ["price", "sqft_price", "date", "delta_lat", "delta_long"]
TARGET = "price"

RANDOM_STATE = 42
TEST_SIZE = 0.3
