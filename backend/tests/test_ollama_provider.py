"""Exercise the real Ollama adapter against HTTP responses, without inference."""

import asyncio
import json

import httpx
import pytest

from app.core.config import settings
from app.services.llm.ollama_provider import OllamaProvider


def mock_ollama(monkeypatch, handler):
    client_class = httpx.AsyncClient
    transport = httpx.MockTransport(handler)
    monkeypatch.setattr(
        httpx, "AsyncClient",
        lambda **kwargs: client_class(transport=transport, **kwargs),
    )


def test_coach_requests_direct_answer_with_bounded_context(monkeypatch):
    def respond(request):
        body = json.loads(request.content)
        assert body["think"] is False
        assert body["options"]["num_ctx"] == 4096
        assert body["messages"][-1]["content"] == "I go yesterday."
        return httpx.Response(200, json={
            "message": {"thinking": "Private reasoning", "content": "Say: I went yesterday."},
            "done_reason": "stop",
        })

    mock_ollama(monkeypatch, respond)
    answer = asyncio.run(OllamaProvider().chat([
        {"role": "user", "content": "I go yesterday."},
    ]))
    assert answer == "Say: I went yesterday."


@pytest.mark.parametrize("data", [
    {"message": {"thinking": "Reasoning only", "content": ""}, "done_reason": "stop"},
    {"message": {"content": "A cut-off answer"}, "done_reason": "length"},
])
def test_incomplete_answer_is_not_saved_as_success(monkeypatch, data):
    mock_ollama(monkeypatch, lambda request: httpx.Response(200, json=data))
    with pytest.raises(RuntimeError):
        asyncio.run(OllamaProvider().chat([{"role": "user", "content": "Hello"}]))


def test_timeout_reports_inference_failure(monkeypatch):
    def timeout(request):
        raise httpx.ReadTimeout("No model response", request=request)

    mock_ollama(monkeypatch, timeout)
    with pytest.raises(TimeoutError, match="120"):
        asyncio.run(OllamaProvider().chat([], {"timeout": 120}))


def test_status_requires_configured_model(monkeypatch):
    mock_ollama(monkeypatch, lambda request: httpx.Response(200, json={
        "models": [{"name": "another-model:latest"}],
    }))
    status = asyncio.run(OllamaProvider().test_connection())
    assert status["available"] is False
    assert status["model"] == settings.OLLAMA_MODEL
    assert status["error"]


def test_learning_tutor_passes_json_schema_to_ollama(monkeypatch):
    from app.schemas.learning import TutorFeedback
    schema = TutorFeedback.model_json_schema()
    def respond(request):
        assert json.loads(request.content)["format"] == schema
        return httpx.Response(200, json={"message":{"content":"{}"},"done_reason":"stop"})
    mock_ollama(monkeypatch, respond)
    assert asyncio.run(OllamaProvider().chat([], {"format":schema})) == "{}"
