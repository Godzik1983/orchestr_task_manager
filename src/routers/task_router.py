"""Роутер CRUD-операций для задач."""

from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Response, status

from src.controllers.task_controller import TaskController
from src.interfaces.task_schemas import (
    TaskCreateSchema,
    TaskListResponseSchema,
    TaskResponseSchema,
    TaskUpdateSchema,
)
from src.modules.tasks.entities import TaskStatus
from src.modules.tasks.repository import TaskRepository
from src.modules.tasks.service import EmptyTaskUpdateError, TaskNotFoundError, TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])

# На данном этапе используем in-memory repository как простой storage.
_repository = TaskRepository()
_service = TaskService(_repository)
_controller = TaskController(_service)


@router.post("/", response_model=TaskResponseSchema, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreateSchema) -> TaskResponseSchema:
    """Создает задачу."""

    return _controller.create_task(payload)


@router.get("/", response_model=TaskListResponseSchema)
def list_tasks(
    status_filter: TaskStatus | None = Query(default=None, alias="status"),
    search: str | None = Query(default=None, alias="search"),
    created_from: datetime | None = Query(default=None, alias="created_from"),
    created_to: datetime | None = Query(default=None, alias="created_to"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
) -> TaskListResponseSchema:
    """Возвращает список задач с фильтрацией и пагинацией."""

    return _controller.list_tasks(
        status=status_filter,
        search=search,
        created_from=created_from,
        created_to=created_to,
        page=page,
        limit=limit,
    )


@router.get("/{task_id}", response_model=TaskResponseSchema)
def get_task(task_id: int) -> TaskResponseSchema:
    """Возвращает задачу по идентификатору."""

    try:
        return _controller.get_task(task_id)
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/{task_id}", response_model=TaskResponseSchema)
def update_task(task_id: int, payload: TaskUpdateSchema) -> TaskResponseSchema:
    """Частично обновляет задачу."""

    try:
        return _controller.update_task(task_id, payload)
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except EmptyTaskUpdateError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int) -> Response:
    """Удаляет задачу."""

    try:
        _controller.delete_task(task_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


def reset_task_module_state() -> None:
    """Сбрасывает in-memory состояние модуля для тестов."""

    _repository.reset()
