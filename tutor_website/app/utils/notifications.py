# app/utils/notifications.py
from typing import Optional
from sqlalchemy.orm import Session

# Простой заглушки для начала
class NotificationManager:
    @staticmethod
    def create_notification(db: Session, user_id: int, title: str, message: str, **kwargs):
        """Создать уведомление (заглушка)"""
        # TODO: Реализовать
        pass

def send_notification(db: Session, user_id: int, title: str, message: str, **kwargs):
    """Отправить уведомление (заглушка)"""
    # TODO: Реализовать
    pass

def get_user_unread_count(db: Session, user_id: int) -> int:
    """Получить количество непрочитанных уведомлений (заглушка)"""
    # TODO: Реализовать
    return 0