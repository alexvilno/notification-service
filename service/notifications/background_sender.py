import asyncio
import logging
import random

from sqlalchemy.ext.asyncio import AsyncSession
from models.notifications import Notification
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
            else:
                notification.status = "failed"

            await self.session.commit()

            return success

        except Exception as e:
            logger.error("Ошибка отправки уведомления: %i", e)
            notification.status = "failed"
            await self.session.commit()

            return False

    @retry(max_attempts=3, delay=0.5)
    async def _send_email(self, notification: Notification) -> bool:
        logger.debug(
            "отправка email-уведомления "
            "id=%d, user=%d, type=%s, message='%.50s'",
            notification.id_notification,
            notification.user_id,
            notification.notification_type,
            notification.message
        )
        await asyncio.sleep(1)
        if random.random() < 0.1:
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
        await asyncio.sleep(0.2)
        if random.random() < 0.1:
            raise Exception("Имитация ошибки отправки в телеграмм")
        return True
