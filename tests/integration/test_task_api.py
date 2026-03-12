"""Integration-тесты API модуля tasks."""

from datetime import timedelta
from pathlib import Path
from urllib.parse import quote
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.app import app
from src.modules.tasks.entities import TaskStatus, utc_now
from src.routers.task_router import configure_task_repository, reset_task_module_state


@pytest.fixture(autouse=True)
def configure_test_db() -> None:
    """Настраивает отдельную SQLite БД для каждого integration-теста."""

    temp_dir = Path("tests/.tmp")
    temp_dir.mkdir(parents=True, exist_ok=True)
    db_path = str(temp_dir / f"integration_{uuid4().hex}.db")
    configure_task_repository(db_path)
    reset_task_module_state()


@pytest.fixture()
def client() -> TestClient:
    """Создает тестовый клиент FastAPI."""

    return TestClient(app)


def test_list_tasks_without_filtering(client: TestClient) -> None:
    """Проверяет list endpoint без фильтрации."""

    client.post("/tasks/", json={"title": "T1"})
    client.post("/tasks/", json={"title": "T2"})

    response = client.get("/tasks/")
    body = response.json()

    assert response.status_code == 200
    assert body["total"] == 2
    assert body["pages"] == 1
    assert len(body["items"]) == 2


def test_list_tasks_with_filtering(client: TestClient) -> None:
    """Проверяет фильтрацию по статусу."""

    client.post("/tasks/", json={"title": "A", "status": TaskStatus.TODO})
    client.post("/tasks/", json={"title": "B", "status": TaskStatus.DONE})
    client.post("/tasks/", json={"title": "C", "status": TaskStatus.DONE})

    response = client.get("/tasks/?status=done")
    body = response.json()

    assert response.status_code == 200
    assert body["total"] == 2
    assert [item["title"] for item in body["items"]] == ["B", "C"]


def test_list_tasks_with_search_filtering(client: TestClient) -> None:
    """Проверяет фильтрацию по поисковому запросу."""

    client.post("/tasks/", json={"title": "Alpha item"})
    client.post("/tasks/", json={"title": "Beta item"})

    response = client.get("/tasks/?search=alpha")
    body = response.json()

    assert response.status_code == 200
    assert body["total"] == 1
    assert [item["title"] for item in body["items"]] == ["Alpha item"]


def test_list_tasks_with_pagination(client: TestClient) -> None:
    """Проверяет пагинацию page/limit."""

    client.post("/tasks/", json={"title": "T1"})
    client.post("/tasks/", json={"title": "T2"})
    client.post("/tasks/", json={"title": "T3"})

    response = client.get("/tasks/?page=2&limit=1")
    body = response.json()

    assert response.status_code == 200
    assert body["total"] == 3
    assert body["pages"] == 3
    assert body["page"] == 2
    assert body["limit"] == 1
    assert [item["title"] for item in body["items"]] == ["T2"]


def test_list_tasks_with_created_from_filter(client: TestClient) -> None:
    """Проверяет фильтрацию по дате создания."""

    client.post("/tasks/", json={"title": "T1"})
    # Будущая дата отсекает все уже созданные задачи.
    created_from = quote((utc_now() + timedelta(days=1)).isoformat())

    response = client.get(f"/tasks/?created_from={created_from}")
    body = response.json()

    assert response.status_code == 200
    assert body["total"] == 0
    assert body["items"] == []


def test_create_update_delete_happy_path(client: TestClient) -> None:
    """Проверяет happy-path для create/update/delete."""

    create_response = client.post("/tasks/", json={"title": "Черновик", "description": "d"})
    created = create_response.json()

    update_response = client.patch(
        f"/tasks/{created['id']}",
        json={"title": "Готово", "status": TaskStatus.DONE},
    )
    updated = update_response.json()

    get_response = client.get(f"/tasks/{created['id']}")
    delete_response = client.delete(f"/tasks/{created['id']}")
    not_found_response = client.get(f"/tasks/{created['id']}")

    assert create_response.status_code == 201
    assert update_response.status_code == 200
    assert updated["title"] == "Готово"
    assert updated["status"] == TaskStatus.DONE
    assert get_response.status_code == 200
    assert delete_response.status_code == 204
    assert not_found_response.status_code == 404
