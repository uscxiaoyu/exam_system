from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Dict

from backend.api import deps
from backend.models.user import User
from backend.models.exam import Exam
from backend.models.section import ExamSection
from backend.db.session import SessionLocal

from pydantic import BaseModel

router = APIRouter()

class SectionAssign(BaseModel):
    marker_id: Optional[int]

class SectionOut(BaseModel):
    id: int
    exam_id: int
    name: str
    section_index: int
    question_range: Optional[str]
    marker_id: Optional[int]

    class Config:
        from_attributes = True

@router.post("/exams/{exam_id}/sync_sections")
def sync_sections(
    exam_id: int,
    config_data: Dict = Body(...), # Expects entire ExamConfig JSON
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Generate ExamSection records based on the JSON config.
    Idempotent: updates existing sections by index or creates new ones.
    """
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    if current_user.school_id and exam.school_id != current_user.school_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    sections_config = config_data.get("sections", [])

    existing_sections = db.query(ExamSection).filter(ExamSection.exam_id == exam_id).all()
    existing_map = {s.section_index: s for s in existing_sections}

    count = 0
    for i, sec_cfg in enumerate(sections_config):
        name = sec_cfg.get("name", f"Section {i+1}")
        num_questions = sec_cfg.get("num_questions", 0)
        q_range = f"{i+1}-1 to {i+1}-{num_questions}" if num_questions > 0 else ""

        if i in existing_map:
            # Update
            s = existing_map[i]
            s.name = name
            s.question_range = q_range
        else:
            # Create
            s = ExamSection(
                exam_id=exam_id,
                name=name,
                section_index=i,
                question_range=q_range
            )
            db.add(s)
            count += 1

    db.commit()
    return {"message": f"Synced {len(sections_config)} sections (Created {count})"}

@router.get("/exams/{exam_id}/sections", response_model=List[SectionOut])
def get_sections(
    exam_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    if current_user.school_id and exam.school_id != current_user.school_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    return db.query(ExamSection).filter(ExamSection.exam_id == exam_id).order_by(ExamSection.section_index).all()

@router.put("/sections/{section_id}/assign")
def assign_marker(
    section_id: int,
    data: SectionAssign,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    section = db.query(ExamSection).filter(ExamSection.id == section_id).first()
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")

    # Verify permission (only exam creator or admin should assign? For now allow any teacher in school)
    exam = db.query(Exam).filter(Exam.id == section.exam_id).first()
    if current_user.school_id and exam.school_id != current_user.school_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Verify marker exists
    if data.marker_id:
        marker = db.query(User).filter(User.id == data.marker_id).first()
        if not marker:
             raise HTTPException(status_code=404, detail="Marker not found")
        if current_user.school_id and marker.school_id != current_user.school_id:
             raise HTTPException(status_code=400, detail="Marker must be in the same school")

    section.marker_id = data.marker_id
    db.commit()
    return {"message": "Marker assigned"}
