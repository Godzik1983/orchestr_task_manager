"""Service-слой модуля auth."""

from datetime import datetime, timezone

from src.interfaces.auth_schemas import UserLoginSchema, UserRegisterSchema
from src.modules.auth.entities import User
from src.modules.auth.repository import AuthRepository
from src.utils.security import create_access_token, decode_access_token, hash_password, verify_password


class UserAlreadyExistsError(Exception):
    """Ошибка повторной регистрации существующего пользователя."""


class InvalidCredentialsError(Exception):
    """Ошибка неверных учетных данных пользователя."""


class InvalidTokenError(Exception):
    """Ошибка некорректного токена аутентификации."""


class AuthService:
    """Сервис бизнес-логики аутентификации пользователей."""

    def __init__(self, repository: AuthRepository) -> None:
        self._repository = repository

    def register(self, payload: UserRegisterSchema) -> User:
        """Регистрирует нового пользователя."""

        existing = self._repository.get_user_by_email(payload.email)
        if existing is not None:
            raise UserAlreadyExistsError("Пользователь с таким email уже существует")

        password_hash = hash_password(payload.password)
        created_at = datetime.now(timezone.utc).isoformat()
        return self._repository.create_user(
            email=payload.email,
            password_hash=password_hash,
            created_at=created_at,
        )

    def login(self, payload: UserLoginSchema) -> str:
        """Проверяет учетные данные и выдает access token."""

        user = self._repository.get_user_by_email(payload.email)
        if user is None or not verify_password(payload.password, user.password_hash):
            raise InvalidCredentialsError("Неверный email или пароль")

        return create_access_token(user_id=user.id, email=user.email)

    def get_current_user(self, token: str) -> User:
        """Возвращает текущего пользователя по JWT токену."""

        try:
            payload = decode_access_token(token)
            user_id = int(payload.get("sub", "0"))
        except Exception as exc:  # noqa: BLE001
            raise InvalidTokenError("Некорректный токен") from exc

        user = self._repository.get_user_by_id(user_id)
        if user is None:
            raise InvalidTokenError("Пользователь из токена не найден")

        return user
