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

def test_upload_standard():
    # Update regex config to ensure it matches our test content
    parser_config = {
        "header_regex": r"ID:(.*?)\s+Name:(.*?)\s+M:(.*)",
        "question_regex": r"(\d+)\.\s*([a-zA-Z0-9_\u4e00-\u9fa5]+)?"
    }
    client.post("/api/settings/parser", json=parser_config)

    header = "ID:000 Name:Std M:0\n"
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
