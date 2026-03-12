"""Точка входа FastAPI-приложения Task Manager."""

from fastapi import FastAPI

from src.routers.health_router import router as health_router
from src.routers.task_router import router as task_router
from src.utils.db import init_tasks_db

app = FastAPI(title="Task Manager API")
# Инициализируем таблицу задач при запуске приложения.
init_tasks_db()

# Подключаем базовые системные роуты.
app.include_router(health_router)
# Подключаем роуты управления задачами.
app.include_router(task_router)
