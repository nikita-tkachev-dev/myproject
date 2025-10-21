Короткие инструкции для AI-агента, работающего с этим репозиторием

Цель: сделать агента продуктивным с минимальным вводом. Фокус — реальные, обнаружимые паттерны в кодовой базе: архитектура, ключевые файлы, команды разработки и соглашения.

- Репозиторий: Flask приложение с фабрикой `create_app` в `app/__init__.py`.
- ORM: SQLAlchemy + Flask-SQLAlchemy (`app/extensions.py` содержит `db`). Миграции: Alembic/Flask-Migrate в `migrations/`.
- Маршруты организованы по Blueprints в папках-фичах: `app/users`, `app/workouts`, `app/exercises`, `app/nutritionlogs`.

Быстрая картинка (inputs / outputs / успех):
- Входные точки: HTTP blueprints (например `exercise_routes` в `app/exercises/routers.py`).
- Персистентность: модели наследуют `db.Model` (например `Exercise`, `User`, `WorkoutSession`).
- Конфиг: `app/config.py` определяет `Config` с окружаемыми значениями для подключения к Postgres; тестовой инфраструктуры специально не найдено.

Главные файлы и почему они важны
- `app/__init__.py` — фабрика приложения: загружает конфиг, инициализирует `db` и `Migrate`, регистрирует blueprints. Любые изменения в регистрациях маршрутов/расширений должны быть отражены здесь.
- `app/config.py` — настройка БД из окружения: переменные `POSTGRES_*` и `SECRET_KEY`.
- `app/extensions.py` — здесь хранится экземпляр `db = SQLAlchemy()`; импортируйте `db` из этого модуля при работе с моделями.
- `migrations/` — alembic миграции; используйте `flask db migrate` / `flask db upgrade` (см. секцию команд).
- Примеры маршрутов/моделей: `app/exercises/models.py` и `app/exercises/routers.py` показывают типичные CRUD-паттерны и обработку ошибок/валидации.

Проектные соглашения и обнаруженные шаблоны
- Feature-first structure: каждая функциональная область — отдельная директория с `models.py` и `routers.py`. Blueprints называются `{feature}_routes` и регистрируются в `create_app`.
- DB-модели используют `db.Enum` для списков (например `muscle_group`, `equipment`, `difficulty`). Значения перечислений хранятся в самой модели как Enum с именами (см. `app/exercises/models.py`).
- Отношения: relationship используют `back_populates` (например `WorkoutExercise` <-> `Exercise`). Имена таблиц указаны через `__tablename__`.
- Роутеры принимают/возвращают JSON: используют `request.get_json()`, `jsonify` и ручную сериализацию полей (например `.value` у Enum — см. `get_exercises`).
- Ошибки при сохранении в БД: pattern — try/except, `db.session.rollback()` при ошибке и возвращение 500 с текстом исключения.

Команды для разработчика (обнаружено в репозитории/требований)
- Создать venv и установить зависимости:
  python -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
- Запуск приложения (мини-руководство):
  export FLASK_APP=app
  export FLASK_ENV=development  # опционально
  # либо использовать фабрику: run через WSGI/Flask как обычно
  flask run
- Миграции (Alembic + Flask-Migrate):
  flask db init   # если миграции ещё не инициализированы (в репозитории уже есть)
  flask db migrate -m "msg"
  flask db upgrade

Важные ограничения и предположения
- Конфигурация ожидает Postgres (см. `SQLALCHEMY_DATABASE_URI` в `app/config.py`) и порт по умолчанию 5532. Локальная БД должна быть доступна или установлены переменные окружения `POSTGRES_*`.
- SECRET_KEY хранится в коде (жёстко задан в `Config`) — при внесении изменений к безопасности: используйте окружение.
- Тестов и CI конфигурации в репозитории явно не обнаружено; добавление тестовой инфраструктуры — полезный следующий шаг.

Примеры задач и как их решать (короткие рецепты для агента)
- Добавить новый endpoint для сущности в feature-папке:
  1) Добавьте/обновите модель в `app/<feature>/models.py` (импорт `db` из `app/extensions.py`).
  2) Добавьте маршруты в `app/<feature>/routers.py` как Blueprint `feature_routes` и регистрируйте их в `app/__init__.py`.
  3) Добавьте миграцию: `flask db migrate -m "add <Feature>"` и `flask db upgrade`.

- Поддерживать сериализацию Enum-полей: используйте `enum_field.value` при формировании JSON-ответа, как в `app/exercises/routers.py`.

Короткие ссылки на файлы-примеры (чтобы копировать/вставлять):
- `app/__init__.py` — фабрика приложения и регистрация blueprints.
- `app/config.py` — подключение к Postgres по `POSTGRES_*`.
- `app/extensions.py` — `db = SQLAlchemy()`.
- `app/exercises/models.py` и `app/exercises/routers.py` — CRUD + Enum пример.

Что не включать/не менять автоматически
- Никогда не коммитить секреты в открытые ветки (SECRET_KEY и пароли). Если агент вносит изменения в конфигурацию, предлагать использовать переменные окружения.

Запрос на уточнение
- Я добавил краткое руководство. Уточните, хотите ли: включить примеры вызовов curl для основных endpoint-ов, или расширить раздел «команды» (например docker-compose, CI)?
