from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class ScheduleStatus(enum.Enum):
    """Статусы занятий"""
    PLANNED = "planned"  # Запланировано
    IN_PROGRESS = "in_progress"  # В процессе
    COMPLETED = "completed"  # Завершено
    CANCELLED = "cancelled"  # Отменено


class Schedule(Base):
    __tablename__ = "schedule"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    student_id = Column(Integer, ForeignKey("users.id"))
    teacher_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    description = Column(String)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(Enum(ScheduleStatus), default=ScheduleStatus.PLANNED)
    is_recurring = Column(Boolean, default=False)
    recurring_pattern = Column(String)  # "daily", "weekly", "monthly"
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")


class RecurringSchedule(Base):
    __tablename__ = "recurring_schedule"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    teacher_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    description = Column(String)
    day_of_week = Column(Integer)  # 0-6 (Monday-Sunday)
    start_time = Column(String)  # "HH:MM"
    duration_minutes = Column(Integer, default=60)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("User", foreign_keys=[student_id])
    teacher = relationship("User", foreign_keys=[teacher_id])