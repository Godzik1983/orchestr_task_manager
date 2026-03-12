"""View-функции модуля auth."""

from src.interfaces.auth_schemas import UserResponseSchema
from src.modules.auth.entities import User


def to_user_response(user: User) -> UserResponseSchema:
    """Преобразует доменную сущность пользователя в API-схему."""

    return UserResponseSchema(
        id=user.id,
        email=user.email,
        created_at=user.created_at,
    )
