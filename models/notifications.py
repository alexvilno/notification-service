from sqlalchemy.orm import declarative_base
from sqlalchemy import CheckConstraint, Column, Index, Integer, Text

BaseModel = declarative_base()


class Notification(BaseModel):
    __tablename__ = "notifications"
    __table_args__ = (
        CheckConstraint(
            "notification_type IN ('email', 'telegram')",
            name="notification_type_check",
        ),
        CheckConstraint(
            "status IN ('pending', 'sent', 'failed')",
            name="notification_status_check",
        ),
        Index("idx_status", "status"),
    )

    id_notification = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="ID уведомления"
    )
    user_id = Column(
        Integer,
        nullable=False,
        comment="ID пользователя"
    )
    message = Column(
        Text,
        nullable=False,
        comment="Текст уведомления"
    )
    notification_type = Column(
        Text,
        nullable=False,
        comment="Тип нотификации (telegram, email)"
    )
    status = Column(
        Text,
        nullable=False,
        comment="Статус нотификации (pending, sent, failed)",
    )
