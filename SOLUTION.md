# Solution: Refactoring the King County Notebook

## How to run

```bash
uv sync                 # install dependencies + the kc_housing package
uv run kc-preprocess    # raw CSV -> data/processed/kc_house_clean.csv
uv run kc-train         # preprocessing + ElasticNet grid search -> model/model.bin
uv run pytest           # run the tests
```

Or use it from Python / a notebook (see `King-County-refactored.ipynb`):

```python
from kc_housing import load_data, preprocess
df = preprocess(load_data())
```

## Structure

| File | What it holds |
|---|---|
| `src/kc_housing/config.py` | Paths and constants that were magic numbers in the notebook |
| `src/kc_housing/data_cleaning.py` | Data Preparation steps, one function each + `clean_data()` |
| `src/kc_housing/feature_engineering.py` | Feature Engineering steps, one function each + `engineer_features()` |
| `src/kc_housing/pipeline.py` | `load_data()`, `preprocess()` and the `kc-preprocess` CLI |
| `src/kc_housing/modeling.py` | Stretch goal: final model, training and saving (`kc-train` CLI) |
| `tests/test_pipeline.py` | Unit tests + a test that the pipeline matches the original notebook code |
| `api/` | Stretch goal: FastAPI CRUD app + Postgres, `Dockerfile`, `docker-compose.yaml`, tests (see `api/README.md`) |

## Answers to the project questions

**What steps did you take to complete the project?**

1. Read the notebook and separated the cells that *change the data* (cleaning, feature
   engineering) from those that only *look at it* (`.info()`, plots, `describe()`).
2. Turned each data-changing step into a small function that takes a DataFrame and
   returns a new one, then chained them with `DataFrame.pipe` into `clean_data()`,
   `engineer_features()` and `preprocess()`.
3. Moved magic numbers (wealth-center coordinates, Earth radius, split settings) into `config.py`.
4. Wrote tests, including one that runs the notebook's original code and checks the
   pipeline produces identical output.
5. Stretch: refactored the final ElasticNet model into `modeling.py` with a CLI (test R² ≈ 0.84).
6. Stretch: built a FastAPI CRUD app for houses (5 features: price, bedrooms, bathrooms,
   sqft_living, grade) backed by Postgres, containerised it with a `Dockerfile` and
   `docker-compose.yaml`, and verified it running in Docker. API tests use SQLite, so they run
   without Docker.

**What challenges did you face?**

- The 33-bedroom row was dropped by hard-coded index `15856`, which breaks on any other
  data. It is now filtered by value (`bedrooms <= 30`).
- `inplace=True` mutated shared state (and is deprecated in current pandas); all functions
  now return copies, so they are safe to re-run.
- The water-distance nested loop made ~3 million Python-level calls. NumPy broadcasting
  computes the same matrix in about a second.
- `water_distance` depends on which waterfront houses are in the data. For new data,
  `add_water_distance` accepts a `reference` set (e.g. the training data's waterfront houses).

**What would you do differently with more time?**

- Wrap the feature engineering in scikit-learn transformers so it lives inside the saved model
  pipeline and the waterfront reference is learned in `fit()`.
- Use a proper haversine distance, and remove dataset-wide steps (water reference) before the
  train/test split to avoid slight leakage.
- Add a `/predict` endpoint to the API that loads the trained model, and CI that runs both test suites.
