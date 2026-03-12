"""Unit-тесты для AuthService."""

from pathlib import Path
from uuid import uuid4

import pytest

from src.interfaces.auth_schemas import UserLoginSchema, UserRegisterSchema
from src.modules.auth.repository import AuthRepository
from src.modules.auth.service import AuthService, InvalidCredentialsError, InvalidTokenError, UserAlreadyExistsError


@pytest.fixture()
def auth_service() -> AuthService:
    """Создает сервис auth с изолированной SQLite БД."""

    temp_dir = Path("tests/.tmp")
    temp_dir.mkdir(parents=True, exist_ok=True)
    db_path = str(temp_dir / f"unit_auth_{uuid4().hex}.db")
    repository = AuthRepository(db_path=db_path)
    repository.reset()
    return AuthService(repository)


def test_register_user_success(auth_service: AuthService) -> None:
    """Проверяет успешную регистрацию пользователя."""

    user = auth_service.register(UserRegisterSchema(email="user@example.com", password="strongpass"))

    assert user.id > 0
    assert user.email == "user@example.com"
    assert user.password_hash


def test_register_duplicate_email_fails(auth_service: AuthService) -> None:
    """Проверяет запрет повторной регистрации одного email."""

    auth_service.register(UserRegisterSchema(email="user@example.com", password="strongpass"))

    with pytest.raises(UserAlreadyExistsError):
        auth_service.register(UserRegisterSchema(email="user@example.com", password="strongpass"))


def test_login_success_and_me(auth_service: AuthService) -> None:
    """Проверяет успешный вход и получение пользователя по токену."""

    auth_service.register(UserRegisterSchema(email="user@example.com", password="strongpass"))
    token = auth_service.login(UserLoginSchema(email="user@example.com", password="strongpass"))
    current_user = auth_service.get_current_user(token)

    assert token
    assert current_user.email == "user@example.com"


def test_login_with_invalid_credentials(auth_service: AuthService) -> None:
    """Проверяет ошибку при неверном пароле."""

    auth_service.register(UserRegisterSchema(email="user@example.com", password="strongpass"))

    with pytest.raises(InvalidCredentialsError):
        auth_service.login(UserLoginSchema(email="user@example.com", password="wrongpass"))


def test_me_with_invalid_token(auth_service: AuthService) -> None:
    """Проверяет ошибку при некорректном токене."""

    with pytest.raises(InvalidTokenError):
        auth_service.get_current_user("invalid.token.value")
