from typing import Literal

from pydantic import BaseModel, Field


class BaseNotificationSchema(BaseModel):
    message: str


class CreateNotificationSchema(BaseNotificationSchema):
    user_id: int
    notification_type: Literal[
        "email",
        "telegram",
    ] = Field(alias="type")


class ResponseNotificationSchema(BaseNotificationSchema):
    id_notification: int
    user_id: int
    notification_type: Literal[
        "email",
        "telegram",
    ] = Field(serialization_alias="type")
    status: str
