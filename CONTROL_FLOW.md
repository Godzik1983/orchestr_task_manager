# CONTROL_FLOW.md

## Сценарий: create_project

Порядок:
1. Прочитать architecture.md
2. Использовать Skill: generate_project_structure
3. Создать базовый app entrypoint
4. Создать базовый health-check route
5. Обновить README при необходимости

---

## Сценарий: add_module

Порядок:
1. Прочитать architecture.md
2. Использовать Skill: generate_module
3. Использовать Skill: generate_crud_routes
4. Использовать Skill: generate_tests
5. Если структура изменилась, использовать Skill: update_architecture

---

## Сценарий: improve_list_endpoint

Порядок:
1. Найти list endpoint
2. Использовать Skill: add_filtering
3. Использовать Skill: add_pagination
4. Использовать Skill: generate_tests
5. Проверить, что README и testing.md остаются актуальными

---

## Сценарий: fix_bugs

Порядок:
1. Использовать Skill: fix_tests
2. Проверить affected files
3. Если исправление затронуло архитектуру, обновить architecture.md
4. Подготовить commit message через Skill: prepare_commit

---

## Сценарий: release_ready

Порядок:
1. Запустить тесты
2. Проверить покрытие
3. Проверить GitHub Actions workflow
4. Обновить документацию
5. Подготовить изменения к коммиту