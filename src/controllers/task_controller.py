"""Контроллер модуля tasks."""

from datetime import datetime

from src.interfaces.task_schemas import (
    TaskCreateSchema,
    TaskListResponseSchema,
    TaskResponseSchema,
    TaskUpdateSchema,
)
from src.modules.tasks.entities import TaskStatus
from src.modules.tasks.service import TaskService
from src.views.task_view import to_task_list_response, to_task_response


class TaskController:
    """Прослойка между роутером и сервисом."""

    def __init__(self, service: TaskService) -> None:
        self._service = service

    def create_task(self, payload: TaskCreateSchema) -> TaskResponseSchema:
        """Создает новую задачу."""

        task = self._service.create_task(
            title=payload.title,
            description=payload.description,
            status=payload.status,
        )
        return to_task_response(task)

    def list_tasks(
        self,
        *,
        status: TaskStatus | None,
        search: str | None,
        created_from: datetime | None,
        created_to: datetime | None,
        page: int,
        limit: int,
    ) -> TaskListResponseSchema:
        """Возвращает список задач с метаданными пагинации."""

        tasks, total = self._service.list_tasks(
            status=status,
            search=search,
            created_from=created_from,
            created_to=created_to,
            page=page,
            limit=limit,
        )
        return to_task_list_response(
            items=tasks,
            total=total,
            page=page,
            limit=limit,
        )

    def get_task(self, task_id: int) -> TaskResponseSchema:
        """Возвращает задачу по идентификатору."""

        return to_task_response(self._service.get_task(task_id))

    def update_task(self, task_id: int, payload: TaskUpdateSchema) -> TaskResponseSchema:
        """Частично обновляет задачу."""

        updates = payload.model_dump(exclude_unset=True)
        return to_task_response(self._service.update_task(task_id, updates))

    def delete_task(self, task_id: int) -> None:
        """Удаляет задачу."""

        self._service.delete_task(task_id)
