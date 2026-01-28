"""
Модуль для фоновых задач
"""

import logging

from core.db import async_session_factory
from schemas.notifications import NotificationSchema
from service.notifications.notification_sender import (
    notification_handler_factory
)
from service.notifications.repository import NotificationRepository

logger = logging.getLogger(__name__)


async def send_notification_background(
        notification_schema: NotificationSchema
):
    """Фоновая задача отправки уведомления"""
    try:
        logger.debug(
                    "Запущена фоновая задача отправки "
                    "%s уведомления notification_id=%i",
                    notification_schema.notification_type,
                    notification_schema.id_notification,
                )
        handler = notification_handler_factory.get_handler(
            notification_type=notification_schema.notification_type
        )
        success: bool = await handler.send(
            notification_schema
        )
        async with async_session_factory() as session:
            repo = NotificationRepository(session)

            notification = await repo.get(
                id_notification=notification_schema.id_notification
            )

            if notification is None:
                logger.error(
                    "Уведомление notification_id=%i не найдено в БД",
                    notification_schema.id_notification
                )
                return

            if success:
                notification.status = "sent"
                logger.info(
                    "Уведомление notification_id=%i успешно отправлено",
                    notification_schema.id_notification,
                )
            else:
                notification.status = "failed"
                logger.warning(
                    "Уведомление notification_id=%i не удалось отправить",
                    notification_schema.id_notification,
                )

            session.add(notification)
            await session.commit()
    except Exception as unexpected_error:
        logger.exception(
            "непредвиденная ошибка при отправке уведомления id=%i: %s",
            notification_schema.id_notification,
            unexpected_error
        )
