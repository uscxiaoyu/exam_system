from fastapi.testclient import TestClient
from backend.main import app
from backend.init_db import init_db
from backend.db.session import SessionLocal

client = TestClient(app)
token = None

def setup_module(module):
    init_db()
    # Login
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "admin123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    global token
    token = response.json()["access_token"]

def test_create_and_get_classes():
    # Create
    response = client.post(
        "/api/v1/classes/",
        json={"name": "Class 1A", "grade": "Grade 10"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Class 1A"
    class_id = data["id"]

    # List
    response = client.get(
        "/api/v1/classes/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    classes = response.json()
    assert len(classes) > 0
    assert any(c["id"] == class_id for c in classes)

def test_import_students():
    # First create a class
    response = client.post(
        "/api/v1/classes/",
        json={"name": "Class 2B", "grade": "Grade 11"},
        headers={"Authorization": f"Bearer {token}"}
    )
    class_id = response.json()["id"]

    # Import CSV
    csv_content = "Name,Student Number\nJohn Doe,S1001\nJane Smith,S1002"
    files = {"file": ("students.csv", csv_content, "text/csv")}

    response = client.post(
        f"/api/v1/classes/{class_id}/students/import",
        files=files,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

    # Verify Students via API
    response = client.get(
        f"/api/v1/students/?class_id={class_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    students = response.json()
    assert len(students) == 2
    assert students[0]["name"] == "John Doe" or students[1]["name"] == "John Doe"
