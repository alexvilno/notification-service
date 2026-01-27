from typing import List, Optional

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.db import get_session
from models.notifications import Notification
from schemas.notifications import CreateNotificationSchema


class NotificationRepository:
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
        return await self.session.get(Notification, id_notification)

    async def get_by_user_id(
        self,
        user_id: int,
        notification_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
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
        ).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())


def get_notification_repository(
    session: AsyncSession = Depends(get_session),
) -> NotificationRepository:
    return NotificationRepository(session)
