from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

class Homework(Base):
    __tablename__ = "homework"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    teacher_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    description = Column(Text)
    file_path = Column(String)
    deadline = Column(DateTime)
    status = Column(String, default="assigned")  # assigned, submitted, reviewed
    grade = Column(Integer)
    feedback = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    submitted_at = Column(DateTime(timezone=True))

    student = relationship("User", foreign_keys=[user_id])
    teacher = relationship("User", foreign_keys=[teacher_id])