"""
Модель сущности уведомления
notifications
"""
from sqlalchemy.orm import declarative_base, mapped_column, Mapped
from sqlalchemy import CheckConstraint, Index, Integer, Text

BaseModel = declarative_base()


class Notification(BaseModel):
    """
    Модель сущности уведомления
    notifications
    """
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

    id_notification: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="ID уведомления"
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="ID пользователя"
    )
    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Текст уведомления"
    )
    notification_type: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Тип нотификации (telegram, email)"
    )
    status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Статус нотификации (pending, sent, failed)",
    )
