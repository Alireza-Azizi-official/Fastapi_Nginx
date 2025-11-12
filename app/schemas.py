from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    username: Annotated[str, Field(min_length=3, max_length=50)]
    email: Annotated[EmailStr, Field()]
    password: Annotated[str, Field(min_length=5, max_length=128)]


class UserOut(BaseModel):
    id: str
    username: str
    email: str
    is_active: bool


class Token(BaseModel):
    access_token: str
    token_type: str


class ItemCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=200)]
    description: Optional[str] = None
    price: Annotated[float, Field(ge=0.0)]
    tags: list[str] = []


class ItemUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    price: Optional[float]
    tags: Optional[list[str]]
