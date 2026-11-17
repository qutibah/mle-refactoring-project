"""Database connection and session handling."""

import os
from collections.abc import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

load_dotenv()

# Postgres in Docker; falls back to a local SQLite file for quick local runs and tests.
DATABASE_URL = os.getenv("DB_CONN", "sqlite:///./houses.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""


def get_db() -> Generator[Session]:
    """Yield one database session per request, then close it."""
    with SessionLocal() as session:
        yield session
