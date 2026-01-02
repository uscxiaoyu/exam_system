from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from backend.api import deps
from backend.models.user import User
from backend.models.exam import Exam
from backend.models.section import ExamSection
from backend.models.exam_record import ExamRecord
from backend.db.session import SessionLocal

router = APIRouter()

@router.get("/pending")
def get_pending_tasks(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Get grading tasks assigned to the current user.
    Returns a list of {exam_name, section_name, pending_count, records: [...]}.
    """
    # 1. Find sections assigned to me
    my_sections = db.query(ExamSection).filter(ExamSection.marker_id == current_user.id).all()
    if not my_sections:
        return []

    tasks = []

    for section in my_sections:
        # Get Exam
        exam = db.query(Exam).filter(Exam.id == section.exam_id).first()
        if not exam: continue

        # Get all records for this exam
        records = db.query(ExamRecord).filter(ExamRecord.exam_id == exam.id).all()

        pending_records = []
        for rec in records:
            details = rec.details_json or {}
            if isinstance(details, str): continue # Skip malformed

            # Check questions in this section
            # Heuristic: section_index i corresponds to section_id "i+1" in details keys like "1-1"
            # We stored section_index in ExamSection (0-based)
            sec_prefix = f"{section.section_index + 1}-"

            # Check if any question in this section is not graded (score is 0 and comment is empty/default?)
            # Or better: check for specific "pending" flag if we set it.
            # Currently logic: if we find a key like "1-1" and it has no score or explicitly marked pending.

            is_pending = False
            for key, val in details.items():
                if key.startswith(sec_prefix):
                    # Check status
                    # If val is float (score), it's graded (maybe 0).
                    # If val is dict (advanced), check 'score'.
                    # Wait, in grade.py we stored record as flat: Q1-1 = score, Q1-1_comment = ...
                    # Or we stored it as simple key-value.

                    # Let's assume fetching "pending" means looking for items where we expect a score but don't have one?
                    # Actually, for subjective questions, we might have set Q1-1 = 0 and Q1-1_comment = "⏳ 待批改"

                    comment_key = f"Q{key}_comment" # History router saves it as Q{key}... wait
                    # History router saves: details_json = {k: v ...}
                    # calculate_score returns: record['Q1-1'] = score, record['Q1-1_comment'] = ...

                    # So in details_json, we look for 'Q{sec_prefix}...'
                    # Wait, ExamRecord.details_json stores what calculate_score returns.

                    q_key = f"Q{key}" # e.g. Q1-1
                    # But keys in details_json might vary depending on how they were saved.
                    # Let's look for any key containing the prefix.

                    # Actually, let's look for the comment field indicating pending.
                    # In grade.py: record[f'Q{q_key}_comment'] = '⏳ 待批改'

                    pass

            # Scan details for "待批改"
            for k, v in details.items():
                if str(v) == "⏳ 待批改":
                    # Check if this key belongs to my section
                    # k is like "Q1-1_comment"
                    if k.startswith(f"Q{sec_prefix}"):
                        is_pending = True
                        break

            if is_pending:
                pending_records.append({
                    "record_id": rec.id,
                    "student_id": rec.student_id,
                    "student_name": rec.student_name
                })

        if pending_records:
            tasks.append({
                "exam_id": exam.id,
                "exam_name": exam.name,
                "section_id": section.id,
                "section_name": section.name,
                "pending_count": len(pending_records),
                "records": pending_records
            })

    return tasks
