from fastapi.testclient import TestClient
from backend.main import app
from backend.init_db import init_db
from backend.db.session import SessionLocal, engine
from backend.models.user import User

client = TestClient(app)

def setup_module(module):
    # Ensure DB is init
    init_db()

def test_login_and_me():
    # Login
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "admin123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    print(response.json())
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert token is not None

    # Get Me
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "admin"
    assert data["role"] == "admin"

def test_login_fail():
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "wrongpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 400
