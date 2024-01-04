"""Contains user schemas."""

from datetime import datetime

from typing import List
from pydantic import BaseModel, EmailStr, Field


class UserSchema(BaseModel):
    id: int
    email: EmailStr
    phone: str | None
    firstname: str
    lastname: str | None
    city: str | None
    links: List[str] | None
    avatar: str | None
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime


class SignInRequestSchema(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=6, max_length=128, serialization_alias="hashed_password"
    )


class SignUpRequestSchema(SignInRequestSchema):
    """Not nullable: email, hashed_password, first_name, is_superuser, is_active"""

    firstname: str
    lastname: str | None


class UserUpdateRequestSchema(BaseModel):
    password: str | None = Field(
        min_length=6, max_length=128, serialization_alias="hashed_password"
    )
    phone: str | None
    firstname: str | None
    lastname: str | None
    city: str | None
    links: List[str] | None
    avatar: str | None
    is_active: bool | None
    is_superuser: bool | None


class UsersListResponseSchema(BaseModel):
    users: List[UserSchema]


class TokenSchema(BaseModel):
    access_token: str
    token_type: str
