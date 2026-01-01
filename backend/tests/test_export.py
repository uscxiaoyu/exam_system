from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_export_grades_endpoint():
    data = [
        {"学号": "101", "姓名": "A", "机号": "01", "总分": 90, "Q1-1": 10},
        {"学号": "102", "姓名": "B", "机号": "02", "总分": 80, "Q1-1": 0}
    ]
    response = client.post("/api/grade/export", json=data)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert response.headers["content-disposition"] == 'attachment; filename=grades.xlsx'
    # Check magic bytes for zip (xlsx is zip)
    assert response.content[:2] == b'PK'
