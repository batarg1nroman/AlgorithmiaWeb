# app/models/notification.py
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database import Base


class NotificationType(enum.Enum):
    """Типы уведомлений"""
    HOMEWORK_ASSIGNED = "homework_assigned"  # Домашнее задание назначено
    HOMEWORK_SUBMITTED = "homework_submitted"  # ДЗ отправлено
    HOMEWORK_REVIEWED = "homework_reviewed"  # ДЗ проверено
    LESSON_SCHEDULED = "lesson_scheduled"  # Урок запланирован
    LESSON_CANCELLED = "lesson_cancelled"  # Урок отменен
    LESSON_REMINDER = "lesson_reminder"  # Напоминание об уроке
    SYSTEM_MESSAGE = "system_message"  # Системное сообщение
    AI_ASSISTANT = "ai_assistant"  # Сообщение от AI ассистента
    KNOWLEDGE_UPDATE = "knowledge_update"  # Обновление в базе знаний
    PAYMENT = "payment"  # Платеж
    OTHER = "other"  # Прочее


class NotificationStatus(enum.Enum):
    """Статусы уведомлений"""
    UNREAD = "unread"  # Не прочитано
    READ = "read"  # Прочитано
    ARCHIVED = "archived"  # В архиве


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Основная информация
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(Enum(NotificationType), default=NotificationType.SYSTEM_MESSAGE)
    status = Column(Enum(NotificationStatus), default=NotificationStatus.UNREAD)

    # Ссылки на связанные сущности (опционально)
    related_entity_type = Column(String(50), nullable=True)  # "homework", "lesson", "payment"
    related_entity_id = Column(Integer, nullable=True)  # ID связанной сущности

    # Метаданные
    priority = Column(Integer, default=1)  # 1-5, где 5 - наивысший приоритет
    is_actionable = Column(Boolean, default=False)  # Требует действия от пользователя
    action_url = Column(String(500), nullable=True)  # URL для действия

    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    read_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    # Связи
    user = relationship("User", back_populates="notifications")


class NotificationSettings(Base):
    __tablename__ = "notification_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    # Настройки email уведомлений
    email_enabled = Column(Boolean, default=True)
    email_homework = Column(Boolean, default=True)
    email_lessons = Column(Boolean, default=True)
    email_system = Column(Boolean, default=True)
    email_promotions = Column(Boolean, default=False)

    # Настройки push-уведомлений
    push_enabled = Column(Boolean, default=True)
    push_homework = Column(Boolean, default=True)
    push_lessons = Column(Boolean, default=True)
    push_system = Column(Boolean, default=True)

    # Настройки SMS уведомлений
    sms_enabled = Column(Boolean, default=False)
    sms_lessons_reminder = Column(Boolean, default=False)
    sms_important = Column(Boolean, default=True)

    # Частота напоминаний
    lesson_reminder_hours = Column(Integer, default=1)  # За сколько часов напоминать об уроке
    homework_reminder_days = Column(Integer, default=1)  # За сколько дней напоминать о ДЗ

    # Временные ограничения
    quiet_start = Column(String(5), default="22:00")  # Начало тихого времени
    quiet_end = Column(String(5), default="08:00")  # Конец тихого времени

    user = relationship("User", back_populates="notification_settings")