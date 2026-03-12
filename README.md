# Task Manager

FastAPI-проект для управления задачами и базовой аутентификации.

## Локальный запуск

1. Создать и активировать виртуальное окружение.
2. Установить зависимости:
`pip install -r requirements.txt`
3. Запустить приложение:
`uvicorn src.app:app --reload`

## Тесты

- Запуск тестов:
`pytest -q`
- Health-check:
`GET /health`

## Встроенный фронтенд

- UI доступен по адресу:
`GET /`
- Статические файлы фронтенда лежат в каталоге:
`src/static`
- Фронтенд использует API этого же сервера:
`/auth/*` и `/tasks/*`

## CD через Docker на VPS

В репозитории добавлен workflow:
- `.github/workflows/deploy.yml`

Он делает:
1. Сборку Docker image из `Dockerfile`.
2. Публикацию image в GitHub Container Registry (GHCR).
3. Деплой на VPS через SSH (`docker compose pull && docker compose up -d`).

### Что подготовить на VPS

1. Установить Docker и Docker Compose plugin:
- `docker --version`
- `docker compose version`
2. Открыть входящий порт `8000` в firewall.
3. Убедиться, что пользователь для деплоя имеет доступ к Docker:
- обычно пользователь в группе `docker`.

### Какие GitHub Secrets нужны

Добавьте в `Settings -> Secrets and variables -> Actions`:
1. `VPS_HOST` - IP или домен VPS.
2. `VPS_USER` - пользователь SSH на VPS.
3. `VPS_PORT` - SSH-порт (обычно `22`).
4. `VPS_SSH_KEY` - приватный SSH-ключ для доступа к VPS.
5. `AUTH_SECRET_KEY` - секрет для подписи JWT в приложении.

### Как запускается деплой

Автоматически:
- на каждый push в `master`.

Вручную:
- через `Actions -> Deploy -> Run workflow`.

### Проверка деплоя

На VPS:
1. `docker ps`
2. `docker logs orchestr_task_manager --tail 100`
3. `curl http://<VPS_HOST>:8000/health`
