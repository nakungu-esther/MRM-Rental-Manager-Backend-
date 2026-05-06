from __future__ import annotations

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: str | None = None


class UserUpdate(BaseModel):
    full_name: str | None = None
    phone: str | None = None


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    phone: str | None = None
    role: str

    model_config = {"from_attributes": True}

