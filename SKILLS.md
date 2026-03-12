# SKILLS.md

## Skill: generate_project_structure

Описание:
Создает структуру Python-проекта по архитектурной схеме.

Что должен сделать:
- создать папки src, modules, controllers, routers, middleware, views, interfaces, utils
- создать папки tests/unit и tests/integration
- создать базовые __init__.py там, где это уместно
- не создавать лишние файлы без необходимости

---

## Skill: generate_module

Описание:
Создает новый модуль приложения по имени сущности.

Что должен сделать:
- создать repository
- создать service
- создать controller
- создать router
- создать schemas / interfaces
- зарегистрировать модуль в приложении
- добавить комментарии на русском языке

Пример:
tasks, users, auth

---

## Skill: generate_crud_routes

Описание:
Создает CRUD-роуты для сущности.

Что должен сделать:
- GET list
- GET by id
- POST create
- PATCH update
- DELETE remove
- предусмотреть фильтрацию и пагинацию там, где это уместно

---

## Skill: add_filtering

Описание:
Добавляет фильтрацию в список сущностей.

Пример:
- status
- completed
- search
- created_from
- created_to

---

## Skill: add_pagination

Описание:
Добавляет пагинацию в list endpoint.

Требования:
- page
- limit
- total
- items
- в тестах проверить корректную разбивку

---

## Skill: generate_tests

Описание:
Создает тесты для нового или измененного кода.

Что должен сделать:
- unit tests для service
- integration tests для router / API
- добавить комментарии на русском языке
- не дублировать бессмысленные тесты

---

## Skill: fix_tests

Описание:
Запускает тесты, анализирует падения и исправляет причину.

Порядок:
1. запустить pytest
2. прочитать traceback
3. исправить код или тесты
4. перезапустить тесты
5. убедиться, что решение не ломает архитектуру

---

## Skill: update_architecture

Описание:
Обновляет architecture.md, если структура проекта изменилась.

Когда использовать:
- появился новый модуль
- добавлен новый слой
- изменилась ответственность слоев
- добавлены внешние интеграции

---

## Skill: prepare_commit

Описание:
Готовит изменения к коммиту.

Что должен сделать:
- проверить git diff
- предложить понятное сообщение коммита
- не коммитить с сообщением вида "fix" или "update"