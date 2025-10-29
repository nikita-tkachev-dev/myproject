# Demo instructions

Подготовка окружения

1. Создать виртуальное окружение и установить зависимости

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Настроить Postgres (или использовать локальный экземпляр) — переменные окружения по умолчанию в `app/config.py`:

```bash
export POSTGRES_USER=your_postrgres_user
export POSTGRES_PASSWORD=your_postgress_password
export POSTGRES_HOST=127.0.0.1
export POSTGRES_PORT=5532
export POSTGRES_DB=mydb
```

3. Применить миграции

```bash
export FLASK_APP=app
flask db upgrade
```

4. Добавить seed-данные

```bash
python scripts/seed_demo.py
```

5. Запустить приложение

```bash
export FLASK_ENV=development
flask run
```

Demo checklist (для презентации)

- [ ] Зарегистрировать пользователя через `/users/register`
- [ ] Выбрать уровень `/users/select-level`
- [ ] Создать тренировочную сессию (через JSON POST на `/workouts/create` или будущий UI)
- [ ] Показать список упражнений `/exercises/all`
