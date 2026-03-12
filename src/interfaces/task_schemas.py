"""Pydantic-схемы модуля tasks."""

from datetime import datetime

from pydantic import BaseModel, Field

from src.modules.tasks.entities import TaskStatus


class TaskCreateSchema(BaseModel):
    """Схема создания задачи."""

    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    status: TaskStatus = TaskStatus.TODO


class TaskUpdateSchema(BaseModel):
    """Схема частичного обновления задачи."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    status: TaskStatus | None = None


class TaskResponseSchema(BaseModel):
    """Схема ответа с одной задачей."""

    id: int
    title: str
    description: str | None
    status: TaskStatus
    created_at: datetime
    updated_at: datetime


class TaskListResponseSchema(BaseModel):
    """Схема ответа для списка задач с пагинацией."""

    items: list[TaskResponseSchema]
    total: int
    page: int
    limit: int
    pages: int
