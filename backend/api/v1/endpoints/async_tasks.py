from fastapi import APIRouter, Depends, HTTPException, Body
from backend.core.celery_app import celery_app
from backend.tasks.grading import grade_exam_task
from backend.api import deps
from backend.models.user import User
from typing import Dict, Any

router = APIRouter()

@router.post("/grade/async")
def trigger_async_grading(
    payload: Dict[str, Any] = Body(...),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Trigger background grading.
    """
    task = grade_exam_task.delay(payload, current_user.id)
    return {"task_id": task.id, "status": "processing"}

@router.get("/tasks/{task_id}")
def get_task_status(task_id: str):
    task_result = celery_app.AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result
    }
    return result
