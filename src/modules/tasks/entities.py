"""Доменная сущность и перечисления модуля tasks."""

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum


class TaskStatus(StrEnum):
    """Допустимые статусы жизненного цикла задачи."""

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


def utc_now() -> datetime:
    """Возвращает текущее UTC-время для метаданных задачи."""

    return datetime.now(timezone.utc)


@dataclass
class Task:
    """Доменная модель задачи."""

    id: int
    title: str
    description: str | None
    status: TaskStatus
    created_at: datetime
    updated_at: datetime

