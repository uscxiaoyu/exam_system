from fastapi.testclient import TestClient
from backend.main import app
import os
import json

client = TestClient(app)

def test_settings_db():
    new_db = {
        "user": "test_user",
        "password": "test_password",
        "host": "test_host",
        "port": 3307,
        "db_name": "test_db"
    }
    response = client.post("/api/settings/db", json=new_db)
    assert response.status_code == 200
    assert response.json()["user"] == "test_user"

    # Check if file written
    with open("backend/config/db_config.json", "r") as f:
        data = json.load(f)
        assert data["user"] == "test_user"

def test_settings_parser():
    new_parser = {
        "header_regex": "H:(.*)",
        "question_regex": "Q:(.*)"
    }
    response = client.post("/api/settings/parser", json=new_parser)
    assert response.status_code == 200

    # Test upload using new parser settings
    # Create fake content matching new regex
    content = b"H: 123 Std 01\nQ: 1 Ans"
    # Actually my regex "H:(.*)" captures 1 group.
    # But core.py expects 3 groups for header.
    # So I should test with a valid 3-group regex if I want upload to succeed.

    valid_parser = {
        "header_regex": r"ID:(.*?)\s+Name:(.*?)\s+M:(.*)",
        "question_regex": r"Q(\d+)\.(.*)"
    }
    client.post("/api/settings/parser", json=valid_parser)

    content = b"ID:001 Name:Test M:01\nQ1. A"

    # We need a config with "Q1." match keyword?
    # No, match_keyword finds the section start.
    # Let's use default exam config (restored) or ensure it matches.
    # Default config has "一、单项选择题".

    # Let's assume we saved Exam Config with "Part 1"
    exam_config = {
        "exam_name": "Test",
        "sections": [
            {"section_id": "1", "match_keyword": "Part 1", "name": "S1", "score": 1, "num_questions": 1, "question_type": "客观题"}
        ]
    }
    client.post("/api/config/", json=exam_config)

    content = b"ID:001 Name:Test M:01\nPart 1\nQ1. A"

    response = client.post(
        "/api/upload/standard",
        files={"file": ("std.txt", content, "text/plain")}
    )
    if response.status_code != 200:
        print(response.json())

    assert response.status_code == 200
    assert "data" in response.json()
    assert response.json()["data"]["1-1"] == "A"
