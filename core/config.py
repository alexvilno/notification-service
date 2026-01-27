import logging
import os
import sys
from typing import Optional
from urllib.parse import quote_plus

from pydantic import BaseModel, Field, SecretStr

from dotenv import load_dotenv
from uvicorn.logging import DefaultFormatter


class PostgresConfig(BaseModel):
    """
    Конфигурация postgreSQL.
    """

    host: str = Field(min_length=1)
    port: int = Field(ge=1, le=65535)
    database: str = Field(min_length=1)
    user: str = Field(min_length=1)
    password: SecretStr = Field(min_length=1)
    pg_schema: Optional[str] = Field(default="public")

    @property
    def async_url(self) -> str:
        """
        Билдер URL для асинхронного драйвера.
        """
        return self._build_url("postgresql+asyncpg://")

    def _build_url(self, scheme: str) -> str:
        """
        Билдер URL для соединения с экранированием спец-символов
        """
        credentials = (
            f"{quote_plus(self.user)}:"
            f"{quote_plus(self.password.get_secret_value())}"
        )
        loc = f"{self.host}:{self.port}"
        url = f"{scheme}{credentials}@{loc}/{self.database}"

        return url


load_dotenv()

pg_config = PostgresConfig(
    host=os.getenv("POSTGRES_HOST"),
    port=int(os.getenv("POSTGRES_PORT")),
    database=os.getenv("POSTGRES_DATABASE"),
    user=os.getenv("POSTGRES_USER"),
    password=SecretStr(os.getenv("POSTGRES_PASSWORD")),
)


def setup_logging():
    """
    Настройка логирования
    """
    default_formatter = DefaultFormatter(
        fmt="%(levelprefix)s %(asctime)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        use_colors=True,
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # хендлер для STDOUT
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(default_formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(handler)

    app_logger = logging.getLogger("notification_service")
    app_logger.setLevel(logging.DEBUG)

    return app_logger
