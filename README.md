# Code Trainer — Backend

Backend API платформы [Code Trainer](../docs/) — сравнение языков программирования через практические задания.

Архитектура и правила разработки: [CONVENTIONS.md](./CONVENTIONS.md).

## Стек

| Слой | Технологии |
|------|------------|
| Runtime | Python 3.12+ |
| Web | FastAPI, Uvicorn |
| БД | PostgreSQL, SQLAlchemy 2 async, Alembic |
| Очередь | Redis |
| DI | dependency-injector |
| Качество | ruff, black, mypy, pre-commit, pytest |

## Быстрый старт (локально)

### 1. Зависимости

```bash
cd fixed/backend
poetry install
pre-commit install
```

### 2. Окружение

```bash
cp .env.example .env
# отредактируйте .env при необходимости
```

### 3. Запуск API (после реализации инфраструктуры)

```bash
poetry run manage api --reload
```

Пока доступен только `GET /health`.

## Команды разработки

```bash
make lint          # ruff + black --check
make lint-fix      # автоисправление
make typecheck     # mypy
make test          # pytest + coverage
make test-unit     # только unit
make pre-commit    # все хуки на всех файлах
```

Или через Poetry напрямую:

```bash
poetry run pytest
poetry run mypy src
poetry run ruff check src tests
poetry run black src tests
```

## Pre-commit

При `git commit` автоматически запускаются:

- ruff (lint + fix)
- black (format)
- mypy (types)
- базовые проверки (yaml, toml, trailing whitespace, private keys)

Ручной прогон:

```bash
pre-commit run --all-files
```

## Структура

```
src/
  core/       settings, DI, FastAPI factory, Either/Result
  features/   вертикальные срезы (catalog, demo, tasks, …)
  shared/     database, execution pipeline, handlers
  workers/    фоновые процессы
tests/
  unit/ integration/ e2e/
```

Подробнее — [CONVENTIONS.md §2](./CONVENTIONS.md#2-структура-репозитория).
