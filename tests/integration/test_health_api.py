"""Integration-тесты базовых системных роутов."""

from fastapi.testclient import TestClient

from src.app import app


def test_health_check_returns_ok_status() -> None:
    """Проверяет успешный ответ health-check endpoint."""

    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
