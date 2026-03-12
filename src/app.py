"""Точка входа FastAPI-приложения Task Manager."""

from fastapi import FastAPI

from src.routers.health_router import router as health_router
from src.routers.task_router import router as task_router

app = FastAPI(title="Task Manager API")
# Подключаем базовые системные роуты.
app.include_router(health_router)
# Подключаем роуты управления задачами.
app.include_router(task_router)
