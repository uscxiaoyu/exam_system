from fastapi import APIRouter, HTTPException, Body, Depends
from fastapi.responses import Response
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from backend.models.old_models import StudentData, ExamConfig, SubjectiveGradingRequest, GradingResult
from backend.services.core import calculate_score
from backend.services.llm import grade_subjective_question
from backend.utils import generate_excel_bytes
from backend.api import deps
from backend.models.user import User
from backend.services.matching import MatchService

router = APIRouter(prefix="/api/grade", tags=["grade"])

@router.post("/export")
async def export_grades(data: List[Dict] = Body(...)):
    if not data:
        raise HTTPException(status_code=400, detail="No data to export")

    try:
        excel_io = generate_excel_bytes(data)
        return Response(
            content=excel_io.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=grades.xlsx"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch")
async def batch_grade(
    payload: Dict[str, Any] = Body(...),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Payload structure:
    {
        "students": [student_parsed_data, ...],
        "standard_key": {key: answer, ...},
        "config": exam_config_object,
        "llm_results": {student_id: {q_key: {score, comment}}} (Optional)
    }
    """
    students = payload.get("students", [])
    standard_key = payload.get("standard_key", {})
    config_data = payload.get("config", {})
    llm_results = payload.get("llm_results", {})

    if not students or not standard_key or not config_data:
        raise HTTPException(status_code=400, detail="Missing required data")

    # Initialize MatchService
    matcher = None
    if current_user.school_id:
        matcher = MatchService(db, current_user.school_id)

    sections = config_data.get("sections", [])
    graded_results = []

    for student in students:
        # Match Student against DB if school context exists
        if matcher:
            ocr_id = student.get("学号")
            ocr_name = student.get("姓名")
            matched_student = matcher.match_student(ocr_id, ocr_name)
            if matched_student:
                # Update info from DB source of truth
                student["学号"] = matched_student.student_number
                student["姓名"] = matched_student.name
                student["_db_id"] = matched_student.id
            else:
                student["_db_match"] = False

        # Get student's specific LLM results if any
        student_llm_data = None
        student_id = student.get("学号")
        if student_id and student_id in llm_results:
             student_llm_data = llm_results[student_id]

        s_llm = student.get("llm_graded", {})
        if student_llm_data:
            s_llm.update(student_llm_data)

        result = calculate_score(student, standard_key, sections, s_llm)
        graded_results.append(result)

    return graded_results

@router.post("/subjective", response_model=GradingResult)
async def grade_subjective(request: SubjectiveGradingRequest):
    success, score, comment = grade_subjective_question(
        question_text=request.question_text,
        reference_answer=request.reference_answer,
        student_answer=request.student_answer,
        max_score=request.max_score,
        grading_criteria=request.grading_criteria,
        api_config=request.llm_config.model_dump(),
        examples=[ex.model_dump() for ex in request.examples] if request.examples else None
    )

    if not success:
        return GradingResult(score=0.0, comment=f"Error: {comment}")

    return GradingResult(score=score, comment=comment)
