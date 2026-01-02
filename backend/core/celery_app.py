from celery import Celery
from backend.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.task_routes = {
    "backend.tasks.grading.grade_exam_task": "main-queue",
}
