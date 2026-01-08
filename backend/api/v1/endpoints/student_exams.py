from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime
from backend.api import deps
from backend.models.user import User
from backend.models.exam import Exam
from backend.models.exam_record import ExamRecord
from backend.models.student import Student

router = APIRouter()

@router.get("/")
def list_student_exams(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    List exams available for the logged-in student.
    """
    # Assuming the student logs in via a User account that is linked to a Student entity
    # or the User.username matches the Student.student_number.

    # 1. Find the Student entity
    student = db.query(Student).filter(Student.student_number == current_user.username).first()
    if not student:
        # If user is admin/teacher testing, return empty or all?
        if current_user.role in ["teacher", "admin"]:
             # Return all active exams for school
             query = db.query(Exam).filter(
                 Exam.school_id == current_user.school_id,
                 Exam.status.in_(["publishing", "finished"])
             )
             return query.all()
        return []

    # 2. Find exams assigned to the student's class
    # Exams must be 'publishing' status
    exams = db.query(Exam).filter(
        Exam.class_id == student.class_id,
        Exam.status.in_(["publishing", "finished"]),
        Exam.school_id == student.school_id
    ).all()

    # Filter by time if needed (client side can also filter, but safer server side)
    # For now return all and let UI show status

    # Also fetch completion status
    results = []
    for exam in exams:
        # Check if submitted
        record = db.query(ExamRecord).filter(
            ExamRecord.exam_id == exam.id,
            ExamRecord.student_id == student.student_number
        ).first()

        exam_dict = {
            "id": exam.id,
            "name": exam.name,
            "start_time": exam.start_time,
            "end_time": exam.end_time,
            "status": "completed" if record else "available"
        }
        if record:
            exam_dict["score"] = record.total_score

        results.append(exam_dict)

    return results

@router.get("/{exam_id}")
def get_student_exam(
    exam_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Get exam questions for taking. Hides answers.
    """
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    # Security: Ensure student is in the class
    # ... (Skipping strict class check for now, assuming list filters correctly, but good to add)

    # Hide answers
    questions = []
    if exam.questions:
        for q in exam.questions:
            q_copy = q.copy()
            if "answer" in q_copy:
                del q_copy["answer"]
            questions.append(q_copy)

    return {
        "id": exam.id,
        "name": exam.name,
        "questions": questions,
        "start_time": exam.start_time,
        "end_time": exam.end_time
    }

@router.post("/{exam_id}/submit")
def submit_exam(
    exam_id: int,
    answers: Dict[str, str] = Body(...), # { "question_id": "answer_val" }
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    student = db.query(Student).filter(Student.student_number == current_user.username).first()
    if not student:
        raise HTTPException(status_code=400, detail="Student profile not found")

    # Check if already submitted
    existing = db.query(ExamRecord).filter(
        ExamRecord.exam_id == exam.id,
        ExamRecord.student_id == student.student_number
    ).first()

    if existing:
         raise HTTPException(status_code=400, detail="Already submitted")

    # Grade objective questions immediately
    total_score = 0.0
    graded_details = {}

    if exam.questions:
        for q in exam.questions:
            qid = str(q.get("id"))
            student_ans = answers.get(qid)
            correct_ans = q.get("answer")
            max_score = float(q.get("score", 0))

            # Simple exact match grading
            is_correct = (student_ans == correct_ans)
            score = max_score if is_correct else 0

            total_score += score
            graded_details[qid] = {
                "student_answer": student_ans,
                "correct_answer": correct_ans,
                "score": score,
                "max_score": max_score
            }

    # Save Record
    record = ExamRecord(
        exam_id=exam.id,
        student_id=student.student_number,
        student_name=student.name,
        total_score=total_score,
        details_json=graded_details,
        machine_id="online" # Marker for online exam
    )
    db.add(record)
    db.commit()

    return {"message": "Submitted successfully", "score": total_score}
