from fastapi.testclient import TestClient
from backend.main import app
import os

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Smart Grading System Pro API is running"}

def test_get_config():
    response = client.get("/api/config/")
    assert response.status_code == 200
    data = response.json()
    assert "exam_name" in data
    assert "sections" in data

def test_save_config():
    new_config = {
        "exam_name": "Test Exam",
        "sections": [
            {
                "section_id": "1",
                "match_keyword": "Test Section",
                "name": "Test Score",
                "score": 10.0,
                "num_questions": 1,
                "question_type": "客观题"
            }
        ]
    }
    response = client.post("/api/config/", json=new_config)
    assert response.status_code == 200
    assert response.json()["exam_name"] == "Test Exam"

    # Restore default (optional, but good practice if using file based)

def test_upload_standard():
    # Mock file content
    content = b"1-1\n1. A"
    # Actually standard answer parser needs config.
    # Let's assume the config is set to match "1-1" or similar structure.
    # The default parser expects "match_keyword" in the text.

    # Let's construct a valid content based on config saved in previous test
    # "学号:000 姓名:Std 机号:0"
    header = "学号:000 姓名:Std 机号:0\n"
    # Previous test saved "Test Section" as match keyword
    body = "Test Section\n1. A"
    content = (header + body).encode('utf-8')

    response = client.post(
        "/api/upload/standard",
        files={"file": ("std.txt", content, "text/plain")}
    )
    if response.status_code != 200:
        print(response.json())
    assert response.status_code == 200
    assert "data" in response.json()
    assert "1-1" in response.json()["data"]
    assert response.json()["data"]["1-1"] == "A"
