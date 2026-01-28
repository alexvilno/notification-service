"""
Модуль для фоновых задач
"""

import logging

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError, MultipleResultsFound

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
                "Запущена фоновая задача отправки "
                "уведомления notification_id=%i",
                notification_id
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

        except MultipleResultsFound as consistency_err:
            logger.critical(
                "найдено несколько уведомлений с id=%i "
                "консистентность данных нарушена", notification_id
            )
            await session.rollback()
            raise RuntimeError(
                f"найдено несколько уведомлений с id={notification_id}"
            ) from consistency_err

        except SQLAlchemyError as db_error:
            logger.error(
                "ошибка базы данных при обработке уведомления с id=%i: %s",
                notification_id, db_error
            )
            await session.rollback()
            raise RuntimeError(
                f"ошибка базы данных "
                f"при обработке уведомления с id={notification_id}: {db_error}"
            ) from db_error

        except Exception as unexpected_error:
            logger.exception(
                "непредвиденная ошибка при отправке уведомления id=%i: %s",
                notification_id,
                unexpected_error
            )
            await session.rollback()
