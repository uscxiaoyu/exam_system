from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
from backend.api import deps
from backend.models.user import User
from backend.models.exam import Exam
from backend.models.exam_record import ExamRecord
from pydantic import BaseModel

router = APIRouter()

class Question(BaseModel):
    id: str
    type: str  # choice, true_false, etc.
    content: str
    options: List[str] = []
    answer: str
    score: float

class ExamCreate(BaseModel):
    name: str
    class_id: Optional[int] = None
    questions: List[Question] = []
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: str = "draft"

class ExamUpdate(BaseModel):
    name: Optional[str] = None
    class_id: Optional[int] = None
    questions: Optional[List[Question]] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[str] = None

@router.post("/")
def create_exam(
    exam_in: ExamCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    if current_user.role not in ["teacher", "admin", "school_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    new_exam = Exam(
        name=exam_in.name,
        creator_id=current_user.id,
        school_id=current_user.school_id if current_user.school_id else 1,
        class_id=exam_in.class_id,
        status=exam_in.status,
        questions=[q.dict() for q in exam_in.questions],
        start_time=exam_in.start_time,
        end_time=exam_in.end_time
    )
    db.add(new_exam)
    db.commit()
    db.refresh(new_exam)
    return new_exam

@router.get("/")
def list_exams(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    if current_user.role not in ["teacher", "admin", "school_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    query = db.query(Exam)
    if current_user.school_id:
        query = query.filter(Exam.school_id == current_user.school_id)

    # Filter by creator or visible? For now show all in school
    return query.all()

@router.get("/{exam_id}")
def get_exam(
    exam_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    if current_user.school_id and exam.school_id != current_user.school_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    return exam

@router.put("/{exam_id}")
def update_exam(
    exam_id: int,
    exam_in: ExamUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    # Permission check
    if current_user.school_id and exam.school_id != current_user.school_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    if exam_in.name is not None:
        exam.name = exam_in.name
    if exam_in.class_id is not None:
        exam.class_id = exam_in.class_id
    if exam_in.questions is not None:
        exam.questions = [q.dict() for q in exam_in.questions]
    if exam_in.start_time is not None:
        exam.start_time = exam_in.start_time
    if exam_in.end_time is not None:
        exam.end_time = exam_in.end_time
    if exam_in.status is not None:
        exam.status = exam_in.status

    db.commit()
    db.refresh(exam)
    return exam

@router.delete("/{exam_id}")
def delete_exam(
    exam_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    if current_user.school_id and exam.school_id != current_user.school_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    db.delete(exam)
    db.commit()
    return {"message": "Exam deleted"}
