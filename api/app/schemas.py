"""Pydantic request/response schemas.

Validation limits mirror the cleaning rules from the kc_housing pipeline
(e.g. no more than 30 bedrooms, grade on the 1-13 King County scale).
"""

from pydantic import BaseModel, ConfigDict, Field


class HouseBase(BaseModel):
    price: float = Field(gt=0, description="Sale price in USD")
    bedrooms: int = Field(ge=0, le=30)
    bathrooms: float = Field(ge=0, le=10)
    sqft_living: int = Field(gt=0, description="Living area in square feet")
    grade: int = Field(ge=1, le=13, description="King County building grade")


class HouseCreate(HouseBase):
    """Body for POST /houses."""


class HouseUpdate(BaseModel):
    """Body for PATCH /houses/{id}: every field is optional."""

    price: float | None = Field(default=None, gt=0)
    bedrooms: int | None = Field(default=None, ge=0, le=30)
    bathrooms: float | None = Field(default=None, ge=0, le=10)
    sqft_living: int | None = Field(default=None, gt=0)
    grade: int | None = Field(default=None, ge=1, le=13)


class HouseOut(HouseBase):
    """Response body for a stored house."""

    model_config = ConfigDict(from_attributes=True)

    id: int
