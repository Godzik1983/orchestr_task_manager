"""Роутер базовой проверки доступности сервиса."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    """Возвращает технический статус приложения."""

    # Простой ответ для мониторинга и smoke-проверок.
    return {"status": "ok"}
