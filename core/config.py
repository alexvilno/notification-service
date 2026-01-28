from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr, field_validator
from typing import Optional
from urllib.parse import quote_plus
import logging
import sys


class PostgresConfig(BaseSettings):
    """
    Конфигурация postgreSQL.
    """

    model_config = SettingsConfigDict(
        env_prefix="POSTGRES_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra='ignore'
    )

    host: str = Field(..., min_length=1)
    port: int = Field(5432, ge=1, le=65535)
    database: str = Field(..., min_length=1)
    user: str = Field(..., min_length=1)
    password: SecretStr = Field(..., min_length=1)
    pg_schema: Optional[str] = Field(default="public")

    @property
    def async_url(self) -> str:
        """
        Билдер URL для асинхронного драйвера
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
        return f"{scheme}{credentials}@{loc}/{self.database}"


class AppConfig(BaseSettings):
    """
    Конфигурация приложения
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra='ignore'
    )

    telegram_sleep: float = Field(default=0.2, gt=0)
    email_sleep: float = Field(default=1.0, gt=0)
    max_retries: int = Field(default=3, ge=1)
    retry_delay: float = Field(default=1.0, gt=0)
    error_probability: float = Field(default=0.1, gt=0, lt=1)
    log_level: str = Field(default="INFO")
    app_host: str = Field(default="localhost")
    app_port: int = Field(default=8080, ge=1, le=65535)


    @classmethod
    @field_validator('log_level', mode='before')
    def validate_log_level(cls, v: str) -> str:
        """Валидация уровня логирования"""
        if v is None:
            return "INFO"

        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        v_upper = v.upper()

        if v_upper not in valid_levels:
            raise ValueError(f'Log level must be one of: {valid_levels}')
        return v_upper


def load_config():
    """
    загрузка конфигурации
    """
    try:
        postgres_config = PostgresConfig() # type: ignore
        application_config = AppConfig() # type: ignore

        logging.basicConfig(
            level=application_config.log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler(sys.stdout)]
        )

        root_logger = logging.getLogger(__name__)
        root_logger.info("Configuration loaded successfully")
        root_logger.debug(
            f"Postgres config: "
            f"{postgres_config.host}:{postgres_config.port}/"
            f"{postgres_config.database}"
        )
        root_logger.debug(f"Log level: {application_config.log_level}")

        return postgres_config, application_config, root_logger

    except Exception as e:
        # логирование ошибок загрузки конфигурации
        logging.basicConfig(
            level=logging.ERROR,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        logging.error(f"Configuration loading failed: {e}")
        sys.exit(1)


# глобальные объекты конфигурации
pg_config, app_config, logger = load_config()