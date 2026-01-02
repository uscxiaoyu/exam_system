from fastapi.testclient import TestClient
from backend.main import app
from backend.init_db import init_db
from backend.db.session import SessionLocal
from backend.models.exam import Exam
from backend.models.exam_record import ExamRecord

client = TestClient(app)
token = None

def setup_module(module):
    init_db()
    # Login to get token
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "admin123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    global token
    token = response.json()["access_token"]

def test_save_and_get_history():
    records = [
        {"学号": "1001", "姓名": "Test Student", "总分": 95, "Q1": "A"}
    ]

    # Save
    response = client.post(
        "/api/history/",
        json={"exam_name": "Test Exam ORM", "records": records},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

    # Get List
    response = client.get(
        "/api/history/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    exams = response.json()
    assert len(exams) > 0
    exam_id = exams[0]["id"]

    # Get Detail
    response = client.get(
        f"/api/history/{exam_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    details = response.json()
    assert len(details) == 1
    assert details[0]["学号"] == "1001"
    assert details[0]["Q1"] == "A"
