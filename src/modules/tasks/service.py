"""Service-слой модуля tasks."""

from datetime import datetime

from src.modules.tasks.entities import Task, TaskStatus
from src.modules.tasks.repository import TaskRepository


class TaskNotFoundError(Exception):
    """Ошибка отсутствующей задачи."""


class EmptyTaskUpdateError(Exception):
    """Ошибка пустого payload при обновлении."""


class TaskService:
    """Сервис бизнес-логики задач."""

    def __init__(self, repository: TaskRepository) -> None:
        self._repository = repository

    def create_task(
        self,
        *,
        title: str,
        description: str | None,
        status: TaskStatus,
    ) -> Task:
        """Создает задачу на основе доменных данных."""

        return self._repository.create(
            title=title,
            description=description,
            status=status,
        )

    def list_tasks(
        self,
        *,
        status: TaskStatus | None,
        search: str | None,
        created_from: datetime | None,
        created_to: datetime | None,
        page: int,
        limit: int,
    ) -> tuple[list[Task], int]:
        """Возвращает задачи по фильтрам и параметрам пагинации."""

        return self._repository.list(
            status=status,
            search=search,
            created_from=created_from,
            created_to=created_to,
            page=page,
            limit=limit,
        )

    def get_task(self, task_id: int) -> Task:
        """Возвращает задачу или бросает доменную ошибку."""

        task = self._repository.get(task_id)
        if task is None:
            raise TaskNotFoundError(f"Задача с id={task_id} не найдена")
        return task

    def update_task(self, task_id: int, updates: dict[str, object]) -> Task:
        """Частично обновляет задачу."""

        if not updates:
            raise EmptyTaskUpdateError("Для обновления нужно передать хотя бы одно поле")

        task = self._repository.update(task_id, **updates)
        if task is None:
            raise TaskNotFoundError(f"Задача с id={task_id} не найдена")
        return task

    def delete_task(self, task_id: int) -> None:
        """Удаляет задачу или бросает доменную ошибку."""

        deleted = self._repository.delete(task_id)
        if not deleted:
            raise TaskNotFoundError(f"Задача с id={task_id} не найдена")
