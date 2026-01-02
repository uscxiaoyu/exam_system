from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.api import deps
from backend.models.user import User
from backend.models.student import Student
from backend.db.session import SessionLocal

from pydantic import BaseModel

router = APIRouter()

class StudentOut(BaseModel):
    id: int
    name: str
    student_number: str
    class_id: int
    school_id: int

    class Config:
        from_attributes = True

@router.get("/", response_model=List[StudentOut])
def get_students(
    class_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    if not current_user.school_id:
        return []

    query = db.query(Student).filter(Student.school_id == current_user.school_id)

    if class_id:
        query = query.filter(Student.class_id == class_id)

    if search:
        # Search by name or number
        query = query.filter((Student.name.contains(search)) | (Student.student_number.contains(search)))

    return query.limit(100).all()
