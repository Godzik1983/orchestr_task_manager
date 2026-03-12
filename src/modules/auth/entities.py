"""Доменная модель пользователя для модуля auth."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    """Доменная сущность пользователя."""

    id: int
    email: str
    password_hash: str
    created_at: datetime
