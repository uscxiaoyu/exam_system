from fastapi.testclient import TestClient
from backend.main import app
from backend.init_db import init_db
from backend.db.session import SessionLocal, engine
from backend.models.user import User
from backend.models.exam import Exam
from backend.models.exam_record import ExamRecord
from backend.models.section import ExamSection

client = TestClient(app)
token = None

def setup_module(module):
    # Reset DB: Drop all tables and recreate
    # This is safer than init_db which only creates if missing
    from backend.db.base import Base
    Base.metadata.drop_all(bind=engine)
    init_db()

    # Login
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "admin123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    global token
    token = response.json()["access_token"]

def teardown_module(module):
    # Optional clean up
    pass

def test_sync_and_assign_sections():
    # 1. Create Exam Wrapper (via history)
    response = client.post(
        "/api/history/",
        json={"exam_name": "Task Exam 1", "records": [{"学号": "123", "Q1-1": "test"}]},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

    # Get Exam ID
    response = client.get("/api/history/", headers={"Authorization": f"Bearer {token}"})
    exams = response.json()
    exam_id = next(e["id"] for e in exams if e["exam_name"] == "Task Exam 1")

    # 2. Sync Sections
    config_data = {
        "sections": [
            {"name": "Part A", "num_questions": 5},
            {"name": "Part B", "num_questions": 2}
        ]
    }
    response = client.post(
        f"/api/v1/exams/{exam_id}/sync_sections",
        json=config_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

    # 3. List Sections
    response = client.get(
        f"/api/v1/exams/{exam_id}/sections",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    sections = response.json()
    assert len(sections) == 2
    sec1_id = sections[0]["id"]

    # 4. Assign Section
    response = client.put(
        f"/api/v1/sections/{sec1_id}/assign",
        json={"marker_id": 1},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

    # 5. Check Pending Tasks (Should be 0 as Q1-1 is "test" not "待批改")
    response = client.get(
        "/api/v1/tasks/pending",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    tasks = response.json()
    # Filter for this specific exam to avoid noise from other tests
    my_exam_tasks = [t for t in tasks if t["exam_name"] == "Task Exam 1"]
    assert len(my_exam_tasks) == 0

def test_pending_task_logic():
    # Setup: Create NEW Exam to ensure isolation
    client.post(
        "/api/history/",
        json={"exam_name": "Task Exam 2", "records": [{"学号": "init", "val": 1}]},
        headers={"Authorization": f"Bearer {token}"}
    )
    response = client.get("/api/history/", headers={"Authorization": f"Bearer {token}"})
    exam_id = next(e["id"] for e in response.json() if e["exam_name"] == "Task Exam 2")

    # Sync Sections
    client.post(
        f"/api/v1/exams/{exam_id}/sync_sections",
        json={"sections": [{"name": "Sec1", "num_questions": 1}]},
        headers={"Authorization": f"Bearer {token}"}
    )

    # Assign Section to Admin (1)
    response = client.get(f"/api/v1/exams/{exam_id}/sections", headers={"Authorization": f"Bearer {token}"})
    sec_id = response.json()[0]["id"]
    client.put(f"/api/v1/sections/{sec_id}/assign", json={"marker_id": 1}, headers={"Authorization": f"Bearer {token}"})

    # Add a pending record
    record_data = {
        "学号": "999",
        "姓名": "Pending Student",
        "Q1-1": 0,
        "Q1-1_comment": "⏳ 待批改"
    }
    client.post(
        "/api/history/",
        json={"exam_name": "Task Exam 2", "records": [record_data]},
        headers={"Authorization": f"Bearer {token}"}
    )

    # Check Pending Tasks
    response = client.get(
        "/api/v1/tasks/pending",
        headers={"Authorization": f"Bearer {token}"}
    )
    tasks = response.json()
    my_exam_tasks = [t for t in tasks if t["exam_name"] == "Task Exam 2"]

    assert len(my_exam_tasks) == 1
    assert my_exam_tasks[0]["pending_count"] == 1
