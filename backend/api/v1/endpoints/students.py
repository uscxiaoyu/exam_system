from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.api import deps
from backend.models.user import User
from backend.models.student import Student
from backend.db.session import SessionLocal
from backend.core import security

from pydantic import BaseModel

router = APIRouter()

class StudentUserSync(BaseModel):
    class_id: int

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

@router.post("/sync-users")
def sync_student_users(
    request: StudentUserSync,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Ensure all students in a class have User accounts.
    """
    students = db.query(Student).filter(Student.class_id == request.class_id).all()
    count = 0
    for s in students:
        existing = db.query(User).filter(User.username == s.student_number).first()
        if not existing:
            new_user = User(
                username=s.student_number,
                password_hash=security.get_password_hash("123456"),
                role="student",
                school_id=s.school_id
            )
            db.add(new_user)
            count += 1
    db.commit()
    return {"message": f"Created {count} user accounts"}
