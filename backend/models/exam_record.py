from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, JSON, DateTime
from sqlalchemy.sql import func
from backend.db.base import Base

class ExamRecord(Base):
    id = Column(Integer, primary_key=True, index=True)

    exam_id = Column(Integer, ForeignKey("exam.id"), nullable=False)
    student_id = Column(String(50), index=True, nullable=False) # Accession/Student Number
    student_name = Column(String(100), nullable=True)
    machine_id = Column(String(50), nullable=True) # If applicable

    total_score = Column(Float, default=0.0)

    # Store detailed answers and scores as JSON for flexibility
    # Structure: {"Q1": "A", "Q1_score": 10, ...} or more structured
    details_json = Column(JSON, nullable=True)

    # Files
    answer_sheet_url = Column(String(512), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
