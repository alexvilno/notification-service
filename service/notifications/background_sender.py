"""
Модуль реализации сервиса фоновых задач
"""
import asyncio
import logging
import random

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import app_config
from core.db import async_session_factory
from models.notifications import Notification
from service.notifications.exceptions import MaxRetriesExceeded
from service.notifications.repository import NotificationRepository
from utils.retry import retry

logger = logging.getLogger(__name__)


class BackgroundNotificationSender:
    """Сервис для отправки уведомлений в фоне"""
    async def send(
            self,
            id_notification,
            user_id,
            message
    ):
        logger.info(
            'called %i %s',
            user_id,
            message
        )
        await asyncio.sleep(1)
        async with async_session_factory() as session:
            repo = NotificationRepository(session=session)
            await repo.update_status(
                id_notification=id_notification,
                status='failed'
            )

        logger.info(
            'done %i %s',
            user_id,
            message
        )


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
