import logging

from sqlalchemy import select

from core.db import async_session_factory
from models.notifications import Notification
from service.notifications.background_sender import (
    BackgroundNotificationSender
)

logger = logging.getLogger(__name__)


async def send_notification_background(notification_id: int):
    """Фоновая задача отправки уведомления"""
    async with async_session_factory() as session:
        try:
            logger.debug(
                "Запущена оновая задача отправки "
                "уведомления notification_id=%i", notification_id
            )
            stmt = select(Notification).where(
                Notification.id_notification == notification_id
            )
            result = await session.execute(stmt)
            notification = result.scalar_one_or_none()

            if not notification:
                logger.error(
                    "Задача с notification_id=%i "
                    "не найдена", notification_id
                )
            sender = BackgroundNotificationSender(session)
            await sender.send(notification)

        except Exception:
            await session.rollback()
