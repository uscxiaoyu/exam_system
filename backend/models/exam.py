from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime, JSON
from sqlalchemy.sql import func
from backend.db.base import Base

class Exam(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=False)

    # Status: draft, publishing, grading, finished
    status = Column(String(20), default="draft")

    creator_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    school_id = Column(Integer, ForeignKey("school.id"), nullable=False)

    # Optional link to a specific class (for auto-roster)
    # Optional link to a specific class (for auto-roster)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=True)

    # Sharing Info
    source_exam_id = Column(Integer, nullable=True) # If copied from another exam
    source_teacher_name = Column(String(100), nullable=True) # Name of original creator

    # Exam Content
    questions = Column(JSON, nullable=True) # List of questions
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
