"""Repository-слой модуля auth."""

from datetime import datetime

from src.modules.auth.entities import User
from src.utils.db import get_connection, init_users_db


class AuthRepository:
    """Репозиторий пользователей для задач аутентификации."""

    def __init__(self, db_path: str | None = None) -> None:
        self._db_path = db_path
        init_users_db(self._db_path)

    @staticmethod
    def _row_to_user(row: object) -> User:
        """Преобразует строку БД в доменную сущность пользователя."""

        row_map = dict(row)
        return User(
            id=row_map["id"],
            email=row_map["email"],
            password_hash=row_map["password_hash"],
            created_at=datetime.fromisoformat(row_map["created_at"]),
        )

    def create_user(self, *, email: str, password_hash: str, created_at: str) -> User:
        """Создает пользователя в базе данных."""

        with get_connection(self._db_path) as connection:
            cursor = connection.execute(
                """
                INSERT INTO users (email, password_hash, created_at)
                VALUES (?, ?, ?)
                """,
                (email, password_hash, created_at),
            )
            connection.commit()
            user_id = cursor.lastrowid

        user = self.get_user_by_id(user_id)
        if user is None:
            raise RuntimeError("Не удалось прочитать пользователя после вставки")
        return user

    def get_user_by_email(self, email: str) -> User | None:
        """Возвращает пользователя по email."""

        with get_connection(self._db_path) as connection:
            row = connection.execute(
                """
                SELECT id, email, password_hash, created_at
                FROM users
                WHERE email = ?
                """,
                (email,),
            ).fetchone()

        return self._row_to_user(row) if row else None

    def get_user_by_id(self, user_id: int) -> User | None:
        """Возвращает пользователя по идентификатору."""

        with get_connection(self._db_path) as connection:
            row = connection.execute(
                """
                SELECT id, email, password_hash, created_at
                FROM users
                WHERE id = ?
                """,
                (user_id,),
            ).fetchone()

        return self._row_to_user(row) if row else None

    def reset(self) -> None:
        """Очищает таблицу пользователей (используется в тестах)."""

        with get_connection(self._db_path) as connection:
            connection.execute("DELETE FROM users")
            connection.commit()
