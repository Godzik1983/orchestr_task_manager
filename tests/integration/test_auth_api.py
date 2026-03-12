"""Integration-тесты API модуля auth."""

from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.app import app
from src.routers.auth_router import configure_auth_repository, reset_auth_module_state


@pytest.fixture(autouse=True)
def configure_test_db() -> None:
    """Настраивает отдельную SQLite БД для каждого integration-теста auth."""

    temp_dir = Path("tests/.tmp")
    temp_dir.mkdir(parents=True, exist_ok=True)
    db_path = str(temp_dir / f"integration_auth_{uuid4().hex}.db")
    configure_auth_repository(db_path)
    reset_auth_module_state()


@pytest.fixture()
def client() -> TestClient:
    """Создает тестовый клиент FastAPI."""

    return TestClient(app)


def test_register_success(client: TestClient) -> None:
    """Проверяет успешную регистрацию пользователя."""

    response = client.post(
        "/auth/register",
        json={"email": "user@example.com", "password": "strongpass"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "user@example.com"
    assert body["id"] > 0


def test_login_success(client: TestClient) -> None:
    """Проверяет успешный логин и выдачу токена."""

    client.post("/auth/register", json={"email": "user@example.com", "password": "strongpass"})
    response = client.post(
        "/auth/login",
        json={"email": "user@example.com", "password": "strongpass"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"


def test_login_invalid_credentials(client: TestClient) -> None:
    """Проверяет ошибку при неверных учетных данных."""

    client.post("/auth/register", json={"email": "user@example.com", "password": "strongpass"})
    response = client.post(
        "/auth/login",
        json={"email": "user@example.com", "password": "wrongpass"},
    )

    assert response.status_code == 401


def test_me_requires_token(client: TestClient) -> None:
    """Проверяет, что endpoint /auth/me требует токен."""

    response = client.get("/auth/me")

    assert response.status_code == 401


def test_me_with_valid_token(client: TestClient) -> None:
    """Проверяет получение текущего пользователя по валидному токену."""

    client.post("/auth/register", json={"email": "user@example.com", "password": "strongpass"})
    login_response = client.post(
        "/auth/login",
        json={"email": "user@example.com", "password": "strongpass"},
    )
    token = login_response.json()["access_token"]

    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["email"] == "user@example.com"
