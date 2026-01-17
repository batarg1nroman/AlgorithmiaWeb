# app/utils/notifications.py
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.notification import Notification, NotificationType, NotificationStatus


class NotificationManager:
    @staticmethod
    def create_notification(
        db: Session,
        user_id: int,
        title: str,
        message: str,
        notification_type: NotificationType = NotificationType.SYSTEM_MESSAGE,
        related_entity_type: Optional[str] = None,
        related_entity_id: Optional[int] = None,
        action_url: Optional[str] = None,
        priority: int = 1,
        is_actionable: bool = False
    ) -> Notification:
        """Создать уведомление"""
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            status=NotificationStatus.UNREAD,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
            action_url=action_url,
            priority=priority,
            is_actionable=is_actionable
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification

    @staticmethod
    def create_lesson_reminder_notification(
        db: Session,
        user_id: int,
        lesson_id: int,
        lesson_title: str,
        lesson_time: datetime
    ) -> Notification:
        """Создать напоминание об уроке"""
        return NotificationManager.create_notification(
            db=db,
            user_id=user_id,
            title="Напоминание об уроке",
            message=f"Урок '{lesson_title}' начнется {lesson_time.strftime('%d.%m.%Y в %H:%M')}",
            notification_type=NotificationType.LESSON_REMINDER,
            related_entity_type="lesson",
            related_entity_id=lesson_id,
            action_url=f"/schedule/{lesson_id}",
            priority=3,
            is_actionable=True
        )


def send_notification(db: Session, user_id: int, title: str, message: str, **kwargs):
    """Отправить уведомление"""
    return NotificationManager.create_notification(
        db=db,
        user_id=user_id,
        title=title,
        message=message,
        **kwargs
    )


def get_user_unread_count(db: Session, user_id: int) -> int:
    """Получить количество непрочитанных уведомлений"""
    return db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.status == NotificationStatus.UNREAD
    ).count()