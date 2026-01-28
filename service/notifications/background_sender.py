"""
Модуль реализации сервиса фоновых задач
"""
import asyncio
import logging
import random

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import app_config
from models.notifications import Notification
from service.notifications.exceptions import MaxRetriesExceeded
from service.notifications.repository import NotificationRepository
from utils.retry import retry

logger = logging.getLogger(__name__)


class BackgroundNotificationSender:
    """Сервис для отправки уведомлений в фоне"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def send(self, notification: Notification) -> bool:
        """Отправка уведомления и обновление статуса"""
        try:
            if notification.notification_type == "email":
                success = await self._send_email(notification)
            elif notification.notification_type == "telegram":
                success = await self._send_telegram(notification)
            else:
                raise ValueError(
                    f"Неверный тип уведомления: "
                    f"{notification.notification_type}"
                )
            logger.debug(
                "отправка уведомления завершена"
                "id=%d, user=%d, type=%s, message='%.50s'",
                notification.id_notification,
                notification.user_id,
                notification.notification_type,
                notification.message
            )

            if success:
                notification.status = "sent"

            await self.session.commit()

            return success

        except ValueError as validation_error:
            logger.error(
                "Ошибка валидации "
                "при отправке уведомления ID=%i: %s",
                notification.id_notification,
                validation_error
            )
            await self._mark_as_failed(notification.id_notification)
            return False

        except (ConnectionError, TimeoutError) as network_error:
            logger.error(
                "ошибка сети при отправке уведомления id=%i: %s",
                notification.id_notification, network_error
            )
            await self._mark_as_failed(notification.id_notification)
            return False
        except MaxRetriesExceeded:
            await self._mark_as_failed(notification.id_notification)
            return False
        except Exception as err:
            logger.exception(
                "непредвиденная ошибка "
                "при отправке уведомления с id=%i : %s",
                notification.id_notification, err
            )
            await self._mark_as_failed(notification.id_notification)
            return False

    async def _mark_as_failed(
            self,
            id_notification: int
    ):
        try:
            repository = NotificationRepository(self.session)
            await repository.update_status(
                id_notification=id_notification,
                status="failed"
            )
        except SQLAlchemyError as db_error:
            logger.error(
                "ошибка БД при "
                "обновлении статуса уведомления id=%i: %s",
                id_notification, db_error
            )
            return False
        except Exception as err:
            logger.exception(
                "непредвиденная ошибка при пометке уведомления id=%i: %s",
                id_notification,
                err
            )
            return False

    @retry(
        max_attempts=app_config.max_retries,
        delay=app_config.retry_delay
    )
    async def _send_email(self, notification: Notification) -> bool:
        logger.debug(
            "отправка email-уведомления "
            "id=%d, user=%d, type=%s, message='%.50s'",
            notification.id_notification,
            notification.user_id,
            notification.notification_type,
            notification.message
        )
        await asyncio.sleep(app_config.email_sleep)
        if random.random() < app_config.error_probability:
            raise Exception("Имитация ошибки отправки по email")
        return True

    @retry(max_attempts=3, delay=0.5)
    async def _send_telegram(self, notification: Notification) -> bool:
        logger.debug(
            "отправка телеграм-уведомления "
            "id=%d, user=%d, type=%s, message='%.50s'",
            notification.id_notification,
            notification.user_id,
            notification.notification_type,
            notification.message
        )
        await asyncio.sleep(app_config.telegram_sleep)
        if random.random() < app_config.error_probability:
            raise Exception("Имитация ошибки отправки в телеграмм")
        return True
