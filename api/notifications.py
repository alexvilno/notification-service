"""
Модуль API эндпоинтов для работы с уведомлениями
"""

from typing import Optional, List, Literal

from fastapi import APIRouter, BackgroundTasks
from fastapi.params import Depends, Query
from starlette import status as status_codes

from core.tasks import send_notification_background
from schemas.notifications import (
    CreateNotificationSchema,
    ResponseNotificationSchema,
)

from service.notifications.repository import (
    get_notification_repository,
    NotificationRepository,
)

notifications_router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


@notifications_router.post(
    path="/",
    summary="Создать новое уведомление",
    description="Создает новое уведомление и добавляет "
                "фоновую задачу для отправки",
    status_code=status_codes.HTTP_201_CREATED,
)
async def create_notification(
    create_schema: CreateNotificationSchema,
    background_tasks: BackgroundTasks,
    repository: NotificationRepository = Depends(get_notification_repository),
):
    """
    Создание нового уведомления.

    Уведомление сохраняется в БД со статусом "pending",
    после чего запускается фоновая задача
    для его отправки. Клиент получает ответ немедленно,
    не дожидаясь завершения отправки.
    """
    notification = await repository.create(create_schema=create_schema)
    background_tasks.add_task(
        send_notification_background, notification.id_notification
    )
    return notification


@notifications_router.get(
    path="/{user_id}",
    summary="Получить уведомления пользователя",
    description="Возвращает уведомления пользователя "
                "с фильтрацией по статусу отправки",
    response_model=List[ResponseNotificationSchema],
    status_code=status_codes.HTTP_200_OK,
)
async def get_user_notifications(
    user_id: int,
    status: Optional[Literal["pending", "sent", "failed"]] = Query(
        None,
        description="Фильтр по статусу уведомления"
    ),
    repository: NotificationRepository = Depends(get_notification_repository),
):
    """
    Возвращает историю уведомлений
    для указанного пользователя с возможностью фильтрации по статусу.
    """
    notifications = await repository.get_by_user_id(
        user_id=user_id,
        status=status
    )
    schemas = [
        ResponseNotificationSchema.model_validate(
            notification, from_attributes=True
        )
        for notification in notifications
    ]
    return schemas
