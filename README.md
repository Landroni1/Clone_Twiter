# Корпоративный сервис микроблогов (Twitter Clone)

Бэкенд корпоративного сервиса микроблогов на FastAPI и PostgreSQL.

## Стек технологий
* **Язык**: Python 3.11
* **Фреймворк**: FastAPI
* **ORM**: SQLAlchemy 2.0 (асинхронный драйвер asyncpg)
* **Схемы и валидация**: Pydantic v2, pydantic-settings
* **База данных**: PostgreSQL 15
* **Веб-сервер / Reverse Proxy**: Nginx (Alpine)
* **Тестирование**: pytest, pytest-asyncio, httpx, aiosqlite
* **Контейнеризация**: Docker, Docker Compose

## Развертывание через Docker Compose

Для сборки и запуска всего стека (PostgreSQL, FastAPI, Nginx) выполните команду:
```bash
docker-compose up -d --build