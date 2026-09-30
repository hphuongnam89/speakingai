from fastapi.testclient import TestClient
from app.main import app
from app.core.database import init_db

client = TestClient(app)

def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "model" in data

def test_create_session():
    init_db()
    with TestClient(app) as session_client:
        response = session_client.post(
            "/api/v1/sessions/",
            json={"mode": "daily", "topic": "Everyday routines"},
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["id"]
        assert data["mode"] == "daily"
        assert data["topic"] == "Everyday routines"
