"""FastAPI CRUD service for King County houses."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import Base, engine, get_db


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Create the tables on startup (instead of at import time)."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="King County Houses API",
    description="Create, read, update and delete houses stored in a database.",
    version="1.0.0",
    lifespan=lifespan,
)

DbSession = Annotated[Session, Depends(get_db)]


def get_house_or_404(db: Session, house_id: int) -> models.House:
    house = db.get(models.House, house_id)
    if house is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"House {house_id} not found.")
    return house


@app.get("/", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/houses", response_model=schemas.HouseOut, status_code=status.HTTP_201_CREATED
)
def create_house(body: schemas.HouseCreate, db: DbSession) -> models.House:
    house = models.House(**body.model_dump())
    db.add(house)
    db.commit()
    db.refresh(house)
    return house


@app.get("/houses", response_model=list[schemas.HouseOut])
def list_houses(db: DbSession, skip: int = 0, limit: int = 100) -> list[models.House]:
    statement = select(models.House).order_by(models.House.id).offset(skip).limit(limit)
    return list(db.scalars(statement))


@app.get("/houses/{house_id}", response_model=schemas.HouseOut)
def read_house(house_id: int, db: DbSession) -> models.House:
    return get_house_or_404(db, house_id)


@app.put("/houses/{house_id}", response_model=schemas.HouseOut)
def replace_house(
    house_id: int, body: schemas.HouseCreate, db: DbSession
) -> models.House:
    """Replace all fields of a house."""
    house = get_house_or_404(db, house_id)
    for field, value in body.model_dump().items():
        setattr(house, field, value)
    db.commit()
    db.refresh(house)
    return house


@app.patch("/houses/{house_id}", response_model=schemas.HouseOut)
def update_house(
    house_id: int, body: schemas.HouseUpdate, db: DbSession
) -> models.House:
    """Update only the fields that are sent."""
    house = get_house_or_404(db, house_id)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(house, field, value)
    db.commit()
    db.refresh(house)
    return house


@app.delete("/houses/{house_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_house(house_id: int, db: DbSession) -> Response:
    db.delete(get_house_or_404(db, house_id))
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
