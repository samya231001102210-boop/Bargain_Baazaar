from pydantic import BaseModel, Field
from typing import Literal

class OfferCreate(BaseModel):
    listing_id: str
    amount: float = Field(gt=0)
    message: str = Field(default="", max_length=500)

class OfferAction(BaseModel):
    action: Literal["accept", "reject", "counter"]
    counter_amount: float | None = Field(default=None, gt=0)
    message: str = Field(default="", max_length=500)
