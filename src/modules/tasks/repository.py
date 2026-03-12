"""Repository-слой модуля tasks."""

from datetime import datetime

from src.modules.tasks.entities import Task, TaskStatus, utc_now

_UNSET = object()


class TaskRepository:
    """In-memory репозиторий задач."""

    def __init__(self) -> None:
        self._items: dict[int, Task] = {}
        self._next_id: int = 1

    def create(self, *, title: str, description: str | None, status: TaskStatus) -> Task:
        """Создает и сохраняет задачу в хранилище."""

        now = utc_now()
        task = Task(
            id=self._next_id,
            title=title,
            description=description,
            status=status,
            created_at=now,
            updated_at=now,
        )
        self._items[task.id] = task
        self._next_id += 1
        return task

    def get(self, task_id: int) -> Task | None:
        """Возвращает задачу по идентификатору."""

        return self._items.get(task_id)

    def list(
        self,
        *,
        status: TaskStatus | None,
        search: str | None,
        created_from: datetime | None,
        created_to: datetime | None,
        page: int,
        limit: int,
    ) -> tuple[list[Task], int]:
        """Возвращает список задач с фильтрацией и пагинацией."""

        tasks = sorted(self._items.values(), key=lambda item: item.id)

        if status is not None:
            tasks = [task for task in tasks if task.status == status]

        if search:
            # Поиск идет по заголовку и описанию без учета регистра.
            query = search.lower()
            tasks = [
                task
                for task in tasks
                if query in task.title.lower() or query in (task.description or "").lower()
            ]

        if created_from is not None:
            # Оставляем задачи, созданные не раньше указанной даты.
            tasks = [task for task in tasks if task.created_at >= created_from]

        if created_to is not None:
            # Оставляем задачи, созданные не позже указанной даты.
            tasks = [task for task in tasks if task.created_at <= created_to]

        total = len(tasks)
        offset = (page - 1) * limit
        paged = tasks[offset : offset + limit]
        return paged, total

    def update(
        self,
        task_id: int,
        *,
        title: str | object = _UNSET,
        description: str | None | object = _UNSET,
        status: TaskStatus | object = _UNSET,
    ) -> Task | None:
        """Обновляет задачу по идентификатору."""

        task = self._items.get(task_id)
        if task is None:
            return None

        if title is not _UNSET:
            task.title = title  # type: ignore[assignment]
        if description is not _UNSET:
            task.description = description  # type: ignore[assignment]
        if status is not _UNSET:
            task.status = status  # type: ignore[assignment]
        task.updated_at = utc_now()
        return task

    def delete(self, task_id: int) -> bool:
        """Удаляет задачу по идентификатору."""

        return self._items.pop(task_id, None) is not None

    def reset(self) -> None:
        """Очищает хранилище (нужно для тестов)."""

        self._items.clear()
        self._next_id = 1
