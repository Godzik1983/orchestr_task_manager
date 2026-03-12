"""Repository-слой модуля tasks на базе SQLite."""

from datetime import datetime

from src.modules.tasks.entities import Task, TaskStatus, utc_now
from src.utils.db import init_tasks_db, get_connection

_UNSET = object()


class TaskRepository:
    """Репозиторий задач, работающий через SQLite."""

    def __init__(self, db_path: str | None = None) -> None:
        self._db_path = db_path
        init_tasks_db(self._db_path)

    @staticmethod
    def _row_to_task(row: object) -> Task:
        """Преобразует строку БД в доменную модель задачи."""

        row_map = dict(row)
        return Task(
            id=row_map["id"],
            title=row_map["title"],
            description=row_map["description"],
            status=TaskStatus(row_map["status"]),
            created_at=datetime.fromisoformat(row_map["created_at"]),
            updated_at=datetime.fromisoformat(row_map["updated_at"]),
        )

    def create(self, *, title: str, description: str | None, status: TaskStatus) -> Task:
        """Создает задачу в базе данных."""

        now = utc_now().isoformat()
        with get_connection(self._db_path) as connection:
            cursor = connection.execute(
                """
                INSERT INTO tasks (title, description, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (title, description, status.value, now, now),
            )
            connection.commit()
            task_id = cursor.lastrowid

        task = self.get(task_id)
        if task is None:
            raise RuntimeError("Не удалось прочитать задачу после вставки в БД")
        return task

    def get(self, task_id: int) -> Task | None:
        """Возвращает задачу по идентификатору."""

        with get_connection(self._db_path) as connection:
            row = connection.execute(
                """
                SELECT id, title, description, status, created_at, updated_at
                FROM tasks
                WHERE id = ?
                """,
                (task_id,),
            ).fetchone()

        return self._row_to_task(row) if row else None

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

        filters: list[str] = []
        params: list[object] = []

        if status is not None:
            filters.append("status = ?")
            params.append(status.value)

        if search:
            filters.append("(LOWER(title) LIKE ? OR LOWER(COALESCE(description, '')) LIKE ?)")
            search_param = f"%{search.lower()}%"
            params.extend([search_param, search_param])

        if created_from is not None:
            filters.append("created_at >= ?")
            params.append(created_from.isoformat())

        if created_to is not None:
            filters.append("created_at <= ?")
            params.append(created_to.isoformat())

        where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""
        offset = (page - 1) * limit

        with get_connection(self._db_path) as connection:
            total = connection.execute(
                f"SELECT COUNT(*) AS total FROM tasks {where_clause}",
                params,
            ).fetchone()["total"]

            rows = connection.execute(
                f"""
                SELECT id, title, description, status, created_at, updated_at
                FROM tasks
                {where_clause}
                ORDER BY id ASC
                LIMIT ? OFFSET ?
                """,
                [*params, limit, offset],
            ).fetchall()

        tasks = [self._row_to_task(row) for row in rows]
        return tasks, total

    def update(
        self,
        task_id: int,
        *,
        title: str | object = _UNSET,
        description: str | None | object = _UNSET,
        status: TaskStatus | object = _UNSET,
    ) -> Task | None:
        """Обновляет задачу по идентификатору."""

        updates: list[str] = []
        params: list[object] = []

        if title is not _UNSET:
            updates.append("title = ?")
            params.append(title)

        if description is not _UNSET:
            updates.append("description = ?")
            params.append(description)

        if status is not _UNSET:
            updates.append("status = ?")
            params.append(status.value)

        if not updates:
            return self.get(task_id)

        updates.append("updated_at = ?")
        params.append(utc_now().isoformat())
        params.append(task_id)

        with get_connection(self._db_path) as connection:
            cursor = connection.execute(
                f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?",
                params,
            )
            connection.commit()
            if cursor.rowcount == 0:
                return None

        return self.get(task_id)

    def delete(self, task_id: int) -> bool:
        """Удаляет задачу по идентификатору."""

        with get_connection(self._db_path) as connection:
            cursor = connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            connection.commit()
            return cursor.rowcount > 0

    def reset(self) -> None:
        """Очищает таблицу задач (используется в тестах)."""

        with get_connection(self._db_path) as connection:
            connection.execute("DELETE FROM tasks")
            connection.commit()
