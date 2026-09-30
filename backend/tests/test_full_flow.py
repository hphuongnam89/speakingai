"""End-to-end API flow using TestClient and the deterministic model stub."""

from fastapi.testclient import TestClient

from app.core.database import SessionLocal
from app.core.config import settings
from app.main import app
from app.repositories.turn_repo import TurnRepository
from app.api import conversation


def test_full_conversation_flow():
    with TestClient(app) as client:
        session_res = client.post(
            "/api/v1/sessions/",
            json={"mode": "daily", "topic": "Food and Cooking"},
        )
        assert session_res.status_code == 200, session_res.text
        session_id = session_res.json()["id"]

        # Voice transcription persists the recognized user turn before asking
        # the coach. The conversation endpoint must reuse it, not duplicate it.
        with SessionLocal() as db:
            TurnRepository(db).create(
                session_id=session_id,
                role="user",
                transcript="She don't like cooking.",
            )

        first_turn = client.post(
            "/api/v1/conversation/respond",
            json={
                "session_id": session_id,
                "user_text": "She don't like cooking.",
                "mode": "daily",
            },
        )
        assert first_turn.status_code == 200, first_turn.text
        first_data = first_turn.json()
        assert first_data["message"]
        assert first_data["corrections"][0]["corrected"] == "She doesn't"
        assert first_data["provider_used"] == "test-stub"

        second_turn = client.post(
            "/api/v1/conversation/respond",
            json={
                "session_id": session_id,
                "user_text": "I usually cook dinner with my family.",
                "mode": "daily",
            },
        )
        assert second_turn.status_code == 200, second_turn.text

        history_res = client.get(f"/api/v1/sessions/{session_id}")
        assert history_res.status_code == 200, history_res.text
        history = history_res.json()
        assert len(history["turns"]) == 4
        assert history["turns"][0]["transcript"] == "She don't like cooking."

        finish_res = client.post(f"/api/v1/sessions/{session_id}/finish")
        assert finish_res.status_code == 200, finish_res.text
        assert finish_res.json()["ended_at"] is not None


def test_conversation_uses_configured_llm_timeout(monkeypatch):
    class TimeoutCaptureRouter:
        options = None

        async def chat_with_metadata(self, messages, options=None):
            self.options = options
            return "That's a clear answer. What happened next?", {
                "provider_used": "test-stub",
                "fallback_triggered": False,
                "latency_ms": 0.0,
            }

    router = TimeoutCaptureRouter()
    monkeypatch.setattr(conversation, "get_model_router", lambda: router)

    with TestClient(app) as client:
        session_res = client.post(
            "/api/v1/sessions/",
            json={"mode": "daily", "topic": "A memorable weekend"},
        )
        assert session_res.status_code == 200, session_res.text
        response = client.post(
            "/api/v1/conversation/respond",
            json={
                "session_id": session_res.json()["id"],
                "user_text": "I went hiking with a friend.",
                "mode": "daily",
            },
        )

    assert response.status_code == 200, response.text
    assert router.options["timeout"] == settings.LLM_TIMEOUT
