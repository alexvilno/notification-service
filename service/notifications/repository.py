"""
Модуль для реализации операций с данными
для уведомлений
"""
import logging
from typing import List, Optional, Literal

from fastapi import Depends
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.db import get_session
from models.notifications import Notification
from schemas.notifications import CreateNotificationSchema

logger = logging.getLogger(__name__)


class NotificationRepository:
    """
    Слой работы с БД с уведомлениями
    """
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
            self,
            create_schema: CreateNotificationSchema
    ) -> Notification:
        """
        Создание уведомления
        """
        notification = Notification(
            user_id=create_schema.user_id,
            message=create_schema.message,
            notification_type=create_schema.notification_type,
            status="pending",
        )
        self.session.add(notification)
        await self.session.commit()
        return notification

    async def get(self, id_notification) -> Optional[Notification]:
        """
        Метод возвращает модель уведомления,
        если запись существует в БД

        :param id_notification: id уведомления
        :return: уведомление, если существует
        """
        return await self.session.get(Notification, id_notification)

    async def update_status(
            self,
            id_notification,
            status: Literal["failed", "sent"]
    ) -> Notification:
        """
        Метод обновляет статус уведомления

        :param id_notification: id уведомления
        :param status: статус (failed, sent)
        :return: модель уведомления
        """
        try:
            logger.debug("апдейт статуса уведомления с id=%i", id_notification)
            notification: Notification = await self.get(id_notification)
            if notification is None:
                raise ValueError(
                    f"уведомление с id={id_notification} не найдено"
                )
            notification.status = status
            self.session.add(notification)
            return notification
        except TypeError as err:
            logger.error(
                "неверный статус уведомления: %s",
                err
            )
            raise ValidationError(
                "неверный статус уведомления"
            ) from err

    async def get_by_user_id(
        self,
        user_id: int,
        notification_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Notification]:
        """Получение уведомлений пользователя с фильтрацией"""
        query = select(Notification).where(Notification.user_id == user_id)

        if notification_type:
            query = query.where(
                Notification.notification_type == notification_type
            )

        if status:
            query = query.where(Notification.status == status)

        query = query.order_by(
            Notification.id_notification.desc()
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())


def get_notification_repository(
    session: AsyncSession = Depends(get_session),
) -> NotificationRepository:
    """
    Зависимость для эндпоинтов FastAPI
    использование: repo = Depends(get_notification_repository)
    :return: Зависимость (Depends) FastAPI
    """
    return NotificationRepository(session)
