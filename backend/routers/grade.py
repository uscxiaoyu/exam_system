from fastapi import APIRouter, HTTPException, Body
from typing import List, Dict, Any
from backend.models import StudentData, ExamConfig, SubjectiveGradingRequest, GradingResult
from backend.services.core import calculate_score
from backend.services.llm import grade_subjective_question

router = APIRouter(prefix="/api/grade", tags=["grade"])

@router.post("/batch")
async def batch_grade(
    payload: Dict[str, Any] = Body(...)
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

    # Reconstruct ExamConfig (not strictly needed for calculation but good for validation)
    # Convert config dict back to list of dicts if needed
    sections = config_data.get("sections", [])

    graded_results = []

    for student in students:
        # Get student's specific LLM results if any
        student_llm_data = None
        # Try to match by student ID (學号)
        student_id = student.get("学号")
        if student_id and student_id in llm_results:
             student_llm_data = llm_results[student_id]

        # Or if the payload structure is flat (handled by frontend),
        # frontend might merge llm results into student object before sending.
        # But for separation, let's assume `calculate_score` takes `llm_graded_data`

        # However, `calculate_score` expects `llm_graded_data` to be a dict of {q_key: result}
        # It's better if the frontend passes the merged state or we merge it here.
        # Let's support `llm_graded` key inside student object as well.

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
        # Return 0 score but with error message as comment
        return GradingResult(score=0.0, comment=f"Error: {comment}")

    return GradingResult(score=score, comment=comment)
