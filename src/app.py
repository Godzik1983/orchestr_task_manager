"""Точка входа FastAPI-приложения Task Manager."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.routers.auth_router import router as auth_router
from src.routers.health_router import router as health_router
from src.routers.task_router import router as task_router
from src.utils.db import init_application_db

app = FastAPI(title="Task Manager API")
# Инициализируем таблицы приложения при запуске.
init_application_db()

# Подключаем раздачу статических файлов фронтенда.
STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Подключаем базовые системные роуты.
app.include_router(health_router)
# Подключаем роуты аутентификации.
app.include_router(auth_router)
# Подключаем роуты управления задачами.
app.include_router(task_router)


@app.get("/", include_in_schema=False)
def frontend_index() -> FileResponse:
    """Возвращает главную страницу встроенного фронтенда."""

    return FileResponse(STATIC_DIR / "index.html")
