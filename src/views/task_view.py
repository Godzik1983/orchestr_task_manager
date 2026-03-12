"""Функции представления задач для API-ответов."""

from src.interfaces.task_schemas import TaskListResponseSchema, TaskResponseSchema
from src.modules.tasks.entities import Task


def to_task_response(task: Task) -> TaskResponseSchema:
    """Преобразует доменную модель задачи в схему ответа."""

    return TaskResponseSchema(
        id=task.id,
        title=task.title,
        description=task.description,
        status=task.status,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


def to_task_list_response(
    *,
    items: list[Task],
    total: int,
    page: int,
    limit: int,
) -> TaskListResponseSchema:
    """Формирует ответ списка задач с метаданными пагинации."""

    pages = (total + limit - 1) // limit if total > 0 else 0
    return TaskListResponseSchema(
        items=[to_task_response(task) for task in items],
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )

