"""Pydantic-схемы для модуля auth."""

from datetime import datetime

from pydantic import BaseModel, Field


class UserRegisterSchema(BaseModel):
    """Схема регистрации пользователя."""

    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8, max_length=128)


class UserLoginSchema(BaseModel):
    """Схема входа пользователя."""

    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=1, max_length=128)


class AuthTokenSchema(BaseModel):
    """Схема ответа с access token."""

    access_token: str
    token_type: str = "bearer"


class UserResponseSchema(BaseModel):
    """Схема ответа с данными пользователя."""

    id: int
    email: str
    created_at: datetime
