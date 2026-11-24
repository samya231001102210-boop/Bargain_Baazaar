from pydantic import BaseModel, Field
from typing import Literal

class ListingCreate(BaseModel):
    title: str = Field(min_length=3, max_length=120)
    description: str = Field(min_length=10, max_length=4000)
    listing_type: Literal["product", "service"]
    category_id: str
    price: float = Field(gt=0)
    condition: str = "new"
    image_urls: list[str] = []
    location: str = ""
    quantity: int = Field(default=1, ge=1)
    negotiable: bool = True

class ListingUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    price: float | None = Field(default=None, gt=0)
    condition: str | None = None
    image_urls: list[str] | None = None
    location: str | None = None
    quantity: int | None = Field(default=None, ge=1)
    negotiable: bool | None = None
    is_active: bool | None = None
