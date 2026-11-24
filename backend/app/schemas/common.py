from pydantic import BaseModel, Field, ConfigDict
from typing import Any

class MessageResponse(BaseModel):
    message: str
    data: Any | None = None

class MongoModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)
