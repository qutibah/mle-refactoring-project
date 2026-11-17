"""SQLAlchemy table definitions."""

from sqlalchemy import Float, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class House(Base):
    """A house sale with five features from the King County dataset."""

    __tablename__ = "houses"

    id: Mapped[int] = mapped_column(primary_key=True)
    price: Mapped[float] = mapped_column(Float)
    bedrooms: Mapped[int] = mapped_column(Integer)
    bathrooms: Mapped[float] = mapped_column(Float)
    sqft_living: Mapped[int] = mapped_column(Integer)
    grade: Mapped[int] = mapped_column(Integer)
