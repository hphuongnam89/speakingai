from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "model" in data

def test_create_session():
    # We would mock db here in a real scenario, but for simple test logic:
    # Assuming the DB is initialized in-memory or we catch failures gracefully
    pass # Add more complex mock-based testing when models/schemas are present
