"""
Схемы для уведомлений
"""
from typing import Literal

from pydantic import BaseModel, Field


class BaseNotificationSchema(BaseModel):
    """
    базовая схема уведомления
    """
    message: str = Field(min_length=1)


class CreateNotificationSchema(BaseNotificationSchema):
    """
    схема создания уведомления
    """
    user_id: int = Field(ge=1)
    notification_type: Literal[
        "email",
        "telegram",
    ] = Field(alias="type")


class NotificationSchema(BaseNotificationSchema):
    """
    схема уведомления с id и статусом
    """
    id_notification: int = Field(ge=1)
    user_id: int = Field(ge=1)
    notification_type: Literal[
        "email",
        "telegram",
    ] = Field(serialization_alias="type")
    status: str
