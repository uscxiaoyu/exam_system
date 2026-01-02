from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from backend.db.base import Base

class Student(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, index=True)
    student_number = Column(String(50), nullable=False, index=True) # e.g. "2023001"

    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    school_id = Column(Integer, ForeignKey("school.id"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
