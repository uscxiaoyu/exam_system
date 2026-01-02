from sqlalchemy.orm import Session
from backend.models.student import Student
from typing import Optional, Tuple

class MatchService:
    def __init__(self, db: Session, school_id: int):
        self.db = db
        self.school_id = school_id

    def match_student(self, ocr_number: Optional[str], ocr_name: Optional[str]) -> Optional[Student]:
        """
        Match a student based on OCR results.
        Prioritizes Student Number. If not exact, tries Name.
        """
        student = None

        # 1. Exact Number Match
        if ocr_number:
            student = self.db.query(Student).filter(
                Student.school_id == self.school_id,
                Student.student_number == ocr_number
            ).first()
            if student:
                return student

        # 2. Exact Name Match (if number match failed or number empty)
        if ocr_name:
            student = self.db.query(Student).filter(
                Student.school_id == self.school_id,
                Student.name == ocr_name
            ).first()
            if student:
                return student

        # 3. Future: Fuzzy match logic here

        return None
