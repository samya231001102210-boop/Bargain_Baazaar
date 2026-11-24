from pydantic import BaseModel, Field

class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=60)
    description: str = Field(default="", max_length=300)
    kind: str = Field(default="both", pattern="^(product|service|both)$")
    image_url: str = ""

class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=60)
    description: str | None = None
    kind: str | None = Field(default=None, pattern="^(product|service|both)$")
    image_url: str | None = None
    is_active: bool | None = None
