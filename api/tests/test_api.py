"""API tests against a throwaway SQLite database (no Docker needed)."""

import os
import tempfile

import pytest

_db_file = os.path.join(tempfile.mkdtemp(), "test.db")
os.environ["DB_CONN"] = f"sqlite:///{_db_file}"

from fastapi.testclient import TestClient  # noqa: E402

from app.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402

HOUSE = {
    "price": 538000.0,
    "bedrooms": 3,
    "bathrooms": 2.25,
    "sqft_living": 2570,
    "grade": 7,
}


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


def test_health(client):
    assert client.get("/").json() == {"status": "ok"}


def test_crud_lifecycle(client):
    created = client.post("/houses", json=HOUSE)
    assert created.status_code == 201
    house_id = created.json()["id"]

    assert client.get(f"/houses/{house_id}").json() == {"id": house_id, **HOUSE}
    assert len(client.get("/houses").json()) == 1

    replaced = client.put(f"/houses/{house_id}", json={**HOUSE, "bedrooms": 4})
    assert replaced.json()["bedrooms"] == 4

    patched = client.patch(f"/houses/{house_id}", json={"price": 600000})
    assert patched.json()["price"] == 600000
    assert patched.json()["bedrooms"] == 4

    assert client.delete(f"/houses/{house_id}").status_code == 204
    assert client.get(f"/houses/{house_id}").status_code == 404


def test_missing_house_returns_404(client):
    assert client.put("/houses/999", json=HOUSE).status_code == 404
    assert client.patch("/houses/999", json={"grade": 8}).status_code == 404
    assert client.delete("/houses/999").status_code == 404


@pytest.mark.parametrize(
    "field,value", [("bedrooms", 33), ("grade", 14), ("price", -1), ("sqft_living", 0)]
)
def test_invalid_values_rejected(client, field, value):
    assert client.post("/houses", json={**HOUSE, field: value}).status_code == 422
