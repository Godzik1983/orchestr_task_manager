"""Unit-тесты для TaskService."""

from datetime import timedelta
from pathlib import Path
from uuid import uuid4

import pytest

from src.modules.tasks.entities import TaskStatus, utc_now
from src.modules.tasks.repository import TaskRepository
from src.modules.tasks.service import EmptyTaskUpdateError, TaskNotFoundError, TaskService


@pytest.fixture()
def service() -> TaskService:
    """Создает сервис с изолированной SQLite БД для unit-тестов."""

    temp_dir = Path("tests/.tmp")
    temp_dir.mkdir(parents=True, exist_ok=True)
    db_path = str(temp_dir / f"unit_{uuid4().hex}.db")
    repository = TaskRepository(db_path=db_path)
    repository.reset()
    return TaskService(repository)


def test_create_and_get_task(service: TaskService) -> None:
    """Проверяет базовый путь создания и получения задачи."""

    created = service.create_task(
        title="Первая задача",
        description="Тест",
        status=TaskStatus.TODO,
    )
    loaded = service.get_task(created.id)

    assert loaded.id == created.id
    assert loaded.title == "Первая задача"
    assert loaded.status == TaskStatus.TODO


def test_list_with_filter_and_pagination(service: TaskService) -> None:
    """Проверяет фильтрацию и пагинацию на уровне сервиса."""

    service.create_task(title="A", description=None, status=TaskStatus.TODO)
    service.create_task(title="B", description=None, status=TaskStatus.DONE)
    service.create_task(title="C", description=None, status=TaskStatus.DONE)

    filtered, filtered_total = service.list_tasks(
        status=TaskStatus.DONE,
        search=None,
        created_from=None,
        created_to=None,
        page=1,
        limit=10,
    )
    paged, paged_total = service.list_tasks(
        status=None,
        search=None,
        created_from=None,
        created_to=None,
        page=2,
        limit=1,
    )

    assert filtered_total == 2
    assert [task.title for task in filtered] == ["B", "C"]
    assert paged_total == 3
    assert [task.title for task in paged] == ["B"]


def test_list_with_search_and_date_filters(service: TaskService) -> None:
    """Проверяет фильтрацию по тексту и диапазону дат."""

    service.create_task(title="Alpha task", description=None, status=TaskStatus.TODO)
    service.create_task(title="Beta", description=None, status=TaskStatus.TODO)

    matched, matched_total = service.list_tasks(
        status=None,
        search="alpha",
        created_from=None,
        created_to=None,
        page=1,
        limit=10,
    )
    no_recent, no_recent_total = service.list_tasks(
        status=None,
        search=None,
        created_from=utc_now() + timedelta(days=1),
        created_to=None,
        page=1,
        limit=10,
    )

    assert matched_total == 1
    assert [task.title for task in matched] == ["Alpha task"]
    assert no_recent_total == 0
    assert no_recent == []


def test_update_with_empty_payload_raises_error(service: TaskService) -> None:
    """Проверяет защиту от пустого PATCH-запроса."""

    task = service.create_task(title="Черновик", description=None, status=TaskStatus.TODO)

    with pytest.raises(EmptyTaskUpdateError):
        service.update_task(task.id, {})


def test_delete_and_get_not_found(service: TaskService) -> None:
    """Проверяет удаление задачи и последующий not found."""

    task = service.create_task(title="Удаляемая", description=None, status=TaskStatus.TODO)
    service.delete_task(task.id)

    with pytest.raises(TaskNotFoundError):
        service.get_task(task.id)
