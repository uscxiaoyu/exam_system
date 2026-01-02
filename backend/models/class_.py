from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from backend.db.base import Base

class Class(Base):
    __tablename__ = "classes" # Avoid "class" keyword

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False) # e.g. "Class 1"
    grade = Column(String(20), nullable=True) # e.g. "Grade 10"

    school_id = Column(Integer, ForeignKey("school.id"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
