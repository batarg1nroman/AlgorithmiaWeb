# app/models/__init__.py
from app.models.user import User
from app.models.schedule import Schedule, RecurringSchedule, ScheduleStatus
from app.models.homework import Homework, HomeworkStatus
from app.models.notification import (
    Notification,
    NotificationType,
    NotificationStatus,
    NotificationSettings
)

__all__ = [
    "User",
    "Schedule",
    "RecurringSchedule",
    "ScheduleStatus",
    "Homework",
    "HomeworkStatus",
    "Notification",
    "NotificationType",
    "NotificationStatus",
    "NotificationSettings",
]
