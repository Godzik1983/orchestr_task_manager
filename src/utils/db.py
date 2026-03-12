"""Утилиты для работы с SQLite базой проекта."""

import os
import sqlite3
from pathlib import Path

DEFAULT_DB_PATH = "tasks.db"


def resolve_db_path(db_path: str | None = None) -> str:
    """Возвращает путь к файлу базы данных."""

    if db_path:
        return db_path
    return os.getenv("TASKS_DB_PATH", DEFAULT_DB_PATH)


def get_connection(db_path: str | None = None) -> sqlite3.Connection:
    """Открывает соединение с SQLite и настраивает доступ к колонкам по имени."""

    resolved = resolve_db_path(db_path)
    Path(resolved).parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(resolved)
    connection.row_factory = sqlite3.Row
    return connection


def init_tasks_db(db_path: str | None = None) -> None:
    """Создает таблицу задач, если она отсутствует."""

    with get_connection(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.commit()


def init_users_db(db_path: str | None = None) -> None:
    """Создает таблицу пользователей, если она отсутствует."""

    with get_connection(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.commit()


def init_application_db(db_path: str | None = None) -> None:
    """Инициализирует все таблицы приложения."""

    init_tasks_db(db_path)
    init_users_db(db_path)
