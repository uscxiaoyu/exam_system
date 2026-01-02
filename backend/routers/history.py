from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import text, desc
from typing import List, Dict, Any
from backend.api import deps
from backend.models.user import User
from backend.models.exam_record import ExamRecord
from backend.models.exam import Exam
from backend.utils import generate_excel_bytes
import json
import pandas as pd
import io

router = APIRouter(prefix="/api/history", tags=["history"])

@router.get("/")
async def get_history_summary(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    # Retrieve all exams for the current user's school
    # If user is admin, maybe see all? For now, filter by school_id if set

    query = db.query(Exam)
    if current_user.school_id:
        query = query.filter(Exam.school_id == current_user.school_id)

    exams = query.order_by(desc(Exam.created_at)).all()

    # Also support legacy "exam_name" string based grouping from ExamRecord if migrated
    # For now, let's assume we want to show 'Exams' table

    result = []
    for exam in exams:
        result.append({
            "exam_name": exam.name,
            "created_at": str(exam.created_at),
            "id": exam.id,
            "status": exam.status
        })
    return result

@router.get("/{exam_id}")
async def get_exam_history(
    exam_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    if current_user.school_id and exam.school_id != current_user.school_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    records = db.query(ExamRecord).filter(ExamRecord.exam_id == exam_id).all()

    final_records = []
    for rec in records:
        ui_rec = {
            "学号": rec.student_id,
            "姓名": rec.student_name,
            "机号": rec.machine_id,
            "总分": rec.total_score,
            "created_at": str(rec.created_at)
        }
        if rec.details_json:
            try:
                # details_json is already a dict if loaded by ORM? or JSON string?
                # SQLAlchemy JSON type returns dict/list usually
                details = rec.details_json if isinstance(rec.details_json, dict) else json.loads(rec.details_json)
                ui_rec.update(details)
            except:
                pass
        final_records.append(ui_rec)
    return final_records

@router.get("/{exam_id}/export")
async def export_exam_history(
    exam_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    records = await get_exam_history(exam_id, db, current_user)
    try:
        excel_io = generate_excel_bytes(records)
        exam = db.query(Exam).filter(Exam.id == exam_id).first()
        filename = f"{exam.name}.xlsx" if exam else f"exam_{exam_id}.xlsx"
        return Response(
            content=excel_io.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from pydantic import BaseModel

class HistorySaveRequest(BaseModel):
    exam_name: str
    records: List[Dict[str, Any]]

@router.post("/")
async def save_history(
    request: HistorySaveRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Saves exam records.
    NOTE: This logic creates a new Exam if it doesn't exist, or appends to it.
    """
    exam_name = request.exam_name
    records = request.records

    if not records:
        return {"message": "No records to save"}

    # Find or Create Exam
    # Only within the user's school
    query = db.query(Exam).filter(Exam.name == exam_name)
    if current_user.school_id:
        query = query.filter(Exam.school_id == current_user.school_id)

    exam = query.first()

    if not exam:
        # Create new exam
        exam = Exam(
            name=exam_name,
            creator_id=current_user.id,
            school_id=current_user.school_id if current_user.school_id else 1, # Fallback to default school
            status="finished"
        )
        db.add(exam)
        db.commit()
        db.refresh(exam)

    # Process Records
    count = 0
    for rec_data in records:
        student_id = rec_data.get("学号") or rec_data.get("student_id")
        if not student_id:
            continue

        student_name = rec_data.get("姓名") or rec_data.get("student_name")
        machine_id = rec_data.get("机号") or rec_data.get("machine_id")
        total_score = rec_data.get("总分") or rec_data.get("total_score")

        # Details: everything else
        details = {k: v for k, v in rec_data.items() if k not in ["学号", "student_id", "姓名", "student_name", "机号", "machine_id", "总分", "total_score"]}

        # Check if record exists for this student in this exam?
        # For simplicity, we can delete old ones or update.
        # Let's delete old one first for this student/exam combo
        db.query(ExamRecord).filter(ExamRecord.exam_id == exam.id, ExamRecord.student_id == student_id).delete()

        new_record = ExamRecord(
            exam_id=exam.id,
            student_id=str(student_id),
            student_name=student_name,
            machine_id=str(machine_id),
            total_score=float(total_score) if total_score is not None else 0.0,
            details_json=details
        )
        db.add(new_record)
        count += 1

    db.commit()
    return {"message": f"Saved {count} records for exam '{exam_name}' (ID: {exam.id})"}

@router.delete("/{exam_id}")
async def delete_history(
    exam_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
         raise HTTPException(status_code=404, detail="Exam not found")

    if current_user.school_id and exam.school_id != current_user.school_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Delete records first
    db.query(ExamRecord).filter(ExamRecord.exam_id == exam_id).delete()
    db.delete(exam)
    db.commit()

    return {"message": f"Deleted exam {exam_id}"}
