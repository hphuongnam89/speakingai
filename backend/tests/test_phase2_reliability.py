import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.turn import TurnModel
from app.models.session import SessionModel
from app.models.profile import ProfileModel

client = TestClient(app)


def test_session_already_finished_rejects_new_turn():
    # Create session via API
    sess_res = client.post("/api/v1/sessions/", json={"mode": "daily"})
    assert sess_res.status_code == 200
    session_id = sess_res.json()["id"]

    # Finish the session
    finish_res = client.post(f"/api/v1/sessions/{session_id}/finish")
    assert finish_res.status_code == 200

    # Try to send a message to the finished session
    resp = client.post(
        "/api/v1/conversation/respond",
        json={"session_id": session_id, "user_text": "Hello I want to speak more"}
    )
    assert resp.status_code == 400
    data = resp.json()
    assert data["detail"]["error_code"] == "SESSION_ALREADY_FINISHED"
    assert data["detail"]["retryable"] is False


def test_session_not_found_returns_structured_error():
    resp = client.post(
        "/api/v1/conversation/respond",
        json={"session_id": f"non-existent-{uuid.uuid4().hex}", "user_text": "Hello"}
    )
    assert resp.status_code == 404
    data = resp.json()
    assert data["detail"]["error_code"] == "SESSION_NOT_FOUND"


def test_idempotent_conversation_turn_retry():
    sess_res = client.post("/api/v1/sessions/", json={"mode": "free"})
    assert sess_res.status_code == 200
    session_id = sess_res.json()["id"]

    req_id = f"turn-req-{uuid.uuid4().hex}"

    # First turn attempt
    resp1 = client.post(
        "/api/v1/conversation/respond",
        json={
            "session_id": session_id,
            "user_text": "I really enjoy reading books every weekend in the garden.",
            "request_id": req_id,
            "correction_level": "none"
        }
    )
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert data1["turn_id"] is not None

    with SessionLocal() as db:
        initial_turn_count = db.query(TurnModel).filter(TurnModel.session_id == session_id).count()
        # Should be 1 user turn + 1 assistant turn = 2
        assert initial_turn_count == 2

    # Second turn attempt with the exact same request_id (simulate client retry)
    resp2 = client.post(
        "/api/v1/conversation/respond",
        json={
            "session_id": session_id,
            "user_text": "I really enjoy reading books every weekend in the garden.",
            "request_id": req_id,
            "correction_level": "none"
        }
    )
    assert resp2.status_code == 200
    data2 = resp2.json()

    # Cached response returned, turn_id matches first turn
    assert data2["turn_id"] == data1["turn_id"]
    assert data2["message"] == data1["message"]
    assert data2["provider_used"] == "cached_idempotent"

    # Database must NOT have duplicated turns
    with SessionLocal() as db:
        final_turn_count = db.query(TurnModel).filter(TurnModel.session_id == session_id).count()
        assert final_turn_count == 2
