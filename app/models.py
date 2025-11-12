from datetime import datetime, timezone
from typing import Optional
from beanie import Document
from pydantic import EmailStr, Field


class User(Document):
    username: str
    email: EmailStr
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))

    class Settings:
        name = "users"


class Item(Document):
    name: str
    description: Optional[str] = None
    owner_id: Optional[str] = None
    price: float = 0.0
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: Optional[datetime] = None
    deleted: bool = False

    class Settings:
        name = "items"
