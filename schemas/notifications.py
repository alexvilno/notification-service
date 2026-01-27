from typing import Literal

from pydantic import BaseModel, Field


class BaseNotificationSchema(BaseModel):
    message: str


class CreateNotificationSchema(BaseNotificationSchema):
    user_id: int
    notification_type: Literal[
        "email",
        "telegram",
    ] = Field(
        alias="type", serialization_alias="type"
    )
