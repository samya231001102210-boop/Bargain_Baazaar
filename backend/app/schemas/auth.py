from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Literal

class RegisterInput(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: Literal["buyer", "seller"] = "buyer"

class LoginInput(BaseModel):
    email: EmailStr
    password: str

class UserOutput(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: str

class TokenOutput(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOutput
