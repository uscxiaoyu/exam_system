from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from backend.db.base import Base

class ExamSection(Base):
    __tablename__ = "exam_sections"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exam.id"), nullable=False)
    name = Column(String(100), nullable=False) # e.g. "Section 1", "Translation"
    section_index = Column(Integer, nullable=False) # 0, 1, 2... to match config index

    # Range description, e.g. "Q1-Q5" or "1-1 to 1-5" (Informational)
    question_range = Column(String(50), nullable=True)

    # Assigned Marker (User)
    marker_id = Column(Integer, ForeignKey("user.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
