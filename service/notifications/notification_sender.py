"""
Модуль реализации отправки уведомлений
в сторонние сервисы
"""
import asyncio
import logging
import random
from abc import ABC, abstractmethod


from core.config import app_config
from schemas.notifications import NotificationSchema
from service.notifications.exceptions import SendError
from utils.retry import retry

logger = logging.getLogger(__name__)


class NotificationHandler(ABC):
    """
    Абстрактный обработчик уведомлений
    """
    @abstractmethod
    async def send(self, notification: NotificationSchema) -> bool:
        """
        Абстрактный метод отправки уведомления
        в сторонний сервис

        :param notification: схема уведомления
        :return: результат отправки (True/False)
        """


class EmailHandler(NotificationHandler):
    """
    Обработчик для отправки уведомления по Email
    """
    @retry(
        app_config.max_retries,
        app_config.retry_delay,
        return_value_on_fail=False
    )
    async def send(self, notification: NotificationSchema) -> bool:
        """
        Метод отправки уведомления по Email

        :param notification: схема уведомления
        :return: результат отправки (True/False)
        """
        await asyncio.sleep(app_config.email_sleep)
        if random.random() < app_config.error_probability:
            raise SendError("Имитация ошибки отправки по email")
        return True



class TelegramHandler(NotificationHandler):
    """
    Обработчик для отправки уведомления в Телеграм
    """
    @retry(
        app_config.max_retries,
        app_config.retry_delay,
        return_value_on_fail=False
    )
    async def send(self, notification: NotificationSchema) -> bool:
        """
       Метод отправки уведомления в Телеграм

       :param notification: схема уведомления
       :return: результат отправки (True/False)
       """
        await asyncio.sleep(app_config.telegram_sleep)
        if random.random() < app_config.error_probability:
            raise SendError("Имитация ошибки отправки по телеграм")
        return True

class NotificationHandlerFactory:
    """
    Фабрика создания обработчиков уведомлений
    """
    def __init__(self):
        self._handlers = {}

    def register_handler(
            self,
            notification_type: str,
            handler: NotificationHandler
    ):
        """
        Регистрирует обработчик для указанного типа уведомлений

        :param notification_type: тип уведомления
        :param handler: обработчик
        :return: None
        """
        self._handlers[notification_type] = handler

    def get_handler(self, notification_type: str) -> NotificationHandler:
        """
        Возвращает обработчик для указанного типа уведомления

        :param notification_type:
        :return: None
        """
        handler = self._handlers.get(notification_type)
        if not handler:
            raise ValueError(
                f"Обработчик для типа {notification_type} не зарегистрирован"
            )
        return handler


notification_handler_factory = NotificationHandlerFactory()
notification_handler_factory.register_handler("email", EmailHandler())
notification_handler_factory.register_handler("telegram", TelegramHandler())
