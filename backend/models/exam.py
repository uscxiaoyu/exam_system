from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime
from sqlalchemy.sql import func
from backend.db.base import Base

class Exam(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=False)

    # Status: draft, publishing, grading, finished
    status = Column(String(20), default="draft")

    creator_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    school_id = Column(Integer, ForeignKey("school.id"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
