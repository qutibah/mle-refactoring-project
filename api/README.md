# King County Houses API

A FastAPI CRUD service for houses stored in Postgres, using five features from the
King County dataset: `price`, `bedrooms`, `bathrooms`, `sqft_living` and `grade`.
Validation follows the cleaning rules from the `kc_housing` pipeline
(for example, more than 30 bedrooms is rejected).

## Endpoints

| Method | Path | Action |
|---|---|---|
| `POST` | `/houses` | Create a house |
| `GET` | `/houses?skip=0&limit=100` | List houses |
| `GET` | `/houses/{id}` | Read one house |
| `PUT` | `/houses/{id}` | Replace all fields |
| `PATCH` | `/houses/{id}` | Update some fields |
| `DELETE` | `/houses/{id}` | Delete a house |

Interactive docs: <http://localhost:8000/docs>

## Run with Docker (API + Postgres)

```bash
cd api
cp .env.example .env
docker compose up --build --wait
# ... use the API ...
docker compose down        # add -v to also delete the database volume
```

## Run locally without Docker

With no `DB_CONN` set, the API uses a local SQLite file (`houses.db`):

```bash
cd api
uv sync
uv run uvicorn app.main:app --reload
```

## Tests

```bash
cd api
uv run pytest
```

## Example

```bash
curl -X POST http://localhost:8000/houses \
  -H "Content-Type: application/json" \
  -d '{"price": 538000, "bedrooms": 3, "bathrooms": 2.25, "sqft_living": 2570, "grade": 7}'
```
