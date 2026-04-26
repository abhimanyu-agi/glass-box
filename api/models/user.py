"""Pydantic schemas for users and auth."""

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    username:  str       = Field(..., min_length=3, max_length=64)
    email:     EmailStr
    full_name: str | None = None
    password:  str       = Field(..., min_length=6, max_length=128)


class UserLogin(BaseModel):
    username: str
    password: str


class UserPublic(BaseModel):
    id:         int
    username:   str
    email:      str | None
    full_name:  str | None
    role:       str
    is_active:  bool
    created_at: datetime | None
    last_login: datetime | None


class Token(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    expires_in:   int  # seconds
    user:         UserPublic