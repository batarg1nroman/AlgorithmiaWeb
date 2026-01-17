# app/models/user.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_teacher = Column(Boolean, default=False)
    phone_number = Column(String, nullable=True)  # Для SMS уведомлений

    # Новые поля для уведомлений
    email_notifications = Column(Boolean, default=True)
    push_notifications = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Добавьте эти связи
    notifications = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    notification_settings = relationship(
        "NotificationSettings",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )