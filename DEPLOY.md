# Деплой backend (VPS)

Стек: Docker Compose — API, PostgreSQL, Redis. Раннеры языков — отдельный compose.

API слушает **только localhost:8000** — с интернета доступ через nginx на frontend.

## Требования

- Docker Engine + Compose v2
- Доступ к `/var/run/docker.sock` (проверка студенческого кода)

## Установка

```bash
sudo apt update && sudo apt install -y git docker.io docker-compose-v2
sudo systemctl enable --now docker

git clone git@github.com:smwatertd/Code-Trainer-Backend.git /opt/code-trainer-backend
cd /opt/code-trainer-backend

cp .env.production.example .env
# Отредактируйте .env: пароль БД, AUTH__SECRET_KEY, CORS__ORIGINS

docker compose --env-file .env -f docker/docker-compose.prod.yml up -d --build
```

## Раннеры (Python, C++, Pascal, Java, C#)

```bash
cd /opt/code-trainer-backend
make prod-runners
```

Первый запуск собирает образы (~5–15 мин).

## Обновление

```bash
cd /opt/code-trainer-backend
git pull
docker compose --env-file .env -f docker/docker-compose.prod.yml up -d --build
make prod-runners
```

## Проверка

```bash
curl -s http://127.0.0.1:8000/api/health
```

## Seed (опционально, только dev/demo)

```bash
docker compose -f docker/docker-compose.prod.yml exec api python -m src.cli seed-dev
```

На production лучше не использовать dev-пароли из seed.

## Порты

| Сервис   | Доступ        |
|----------|---------------|
| API      | 127.0.0.1:8000 |
| Postgres | только docker-сеть |
| Redis    | только docker-сеть |
