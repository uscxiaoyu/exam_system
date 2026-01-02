from unittest.mock import MagicMock, patch
from backend.tasks.grading import grade_exam_task

def test_celery_task_mock():
    # Mocking celery behavior since we don't have a worker running in test env
    # But we can import the task function and run it synchronously if we bypass the @task decorator
    # or just test the logic inside if extracted.

    # Actually, we can test that calling .delay returns a mock
    with patch('backend.tasks.grading.grade_exam_task.delay') as mock_delay:
        mock_task = MagicMock()
        mock_task.id = "123"
        mock_delay.return_value = mock_task

        from backend.api.v1.endpoints.async_tasks import trigger_async_grading

        # Mock payload and user
        mock_user = MagicMock()
        mock_user.id = 1

        result = trigger_async_grading({"test": "data"}, mock_user)
        assert result["task_id"] == "123"
        assert result["status"] == "processing"
