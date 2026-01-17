from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class HomeworkStatus(enum.Enum):
    """Статусы домашних заданий"""
    ASSIGNED = "assigned"  # Назначено
    IN_PROGRESS = "in_progress"  # В процессе
    SUBMITTED = "submitted"  # Отправлено
    REVIEWED = "reviewed"  # Проверено
    LATE = "late"  # Просрочено


class Homework(Base):
    __tablename__ = "homework"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    teacher_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    description = Column(Text)
    attachment_path = Column(String)  # Файл задания от преподавателя
    submission_path = Column(String)  # Файл решения от студента
    due_date = Column(DateTime, nullable=False)
    status = Column(Enum(HomeworkStatus), default=HomeworkStatus.ASSIGNED)
    grade = Column(Integer, nullable=True)
    feedback = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    submitted_date = Column(DateTime(timezone=True), nullable=True)

    student = relationship("User", foreign_keys=[user_id])
    teacher = relationship("User", foreign_keys=[teacher_id])