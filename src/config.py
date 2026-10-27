import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Класс конфигурации приложения.

    Автоматически считывает переменные окружения ОС или значения из файла .env.
    Если переменная не задана в окружении, берется дефолтное значение.
    """

    DB_USER: str = Field(default="postgres", description="Имя пользователя БД")
    DB_PASSWORD: str = Field(
        default="postgres_password", description="Пароль пользователя БД"
    )
    DB_HOST: str = Field(default="localhost", description="Хост БД (в Docker: 'db')")
    DB_PORT: int = Field(default=5432, description="Порт PostgreSQL")
    DB_NAME: str = Field(default="database", description="Имя базы данных")
    DB_ECHO: bool = Field(
        default=False, description="Логирование SQL-запросов SQLAlchemy в консоль"
    )

    APP_HOST: str = Field(default="0.0.0.0", description="Хост запуска Uvicorn")
    APP_PORT: int = Field(default=8000, description="Порт запуска Uvicorn")
    APP_TITLE: str = Field(
        default="Corporate Microblogging Service API", description="Название в Swagger"
    )
    APP_VERSION: str = Field(default="1.0.0", description="Версия API")

    UPLOAD_DIR: str = Field(
        default=os.path.join("static", "uploads"),
        description="Физический путь для сохранения медиафайлов",
    )
    STATIC_URL_PREFIX: str = Field(
        default="/static/uploads",
        description="URL-префикс для отдачи картинок фронтенду",
    )

    @property
    def database_url(self) -> str:
        """
        Динамически собирает асинхронный DSN-адрес для SQLAlchemy + asyncpg.
        """
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )


settings = Settings()
