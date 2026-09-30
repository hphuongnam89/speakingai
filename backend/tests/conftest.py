"""Keep the default test suite isolated from app data and external LLM services."""

import os
import sys
import tempfile
from pathlib import Path

import pytest


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

TEST_DB_PATH = Path(tempfile.gettempdir()) / f"ielts-speaking-tests-{os.getpid()}.db"
os.environ.update({
    "DATABASE_URL": f"sqlite:///{TEST_DB_PATH.as_posix()}",
    "ENVIRONMENT": "testing",
    "API_KEY_ENABLED": "false",
    "RATE_LIMIT_ENABLED": "false",
    "SENTRY_DSN": "",
})


class StubModelRouter:
    """Predictable model responses for API behavior tests; no Ollama required."""

    async def chat(self, messages, options=None):
        prompt = "\n".join(message.get("content", "") for message in messages)

        if "ADAPTIVE_PLAN" in prompt:
            return (
                '[ADAPTIVE_PLAN]{"today_objective":"Practice accurate past tense '
                'storytelling.","top_weaknesses":["Past tense accuracy"],'
                '"recommended_topic":"A memorable weekend",'
                '"challenge_phrases":["When I visited...","I had never seen..."]}'
                '[/ADAPTIVE_PLAN]'
            )

        if "EVALUATION" in prompt:
            return (
                '[EVALUATION]{"overall_band":6.5,"fluency_score":6.5,'
                '"fluency_feedback":"Answers are connected and relevant.",'
                '"lexical_score":6.0,"lexical_feedback":"Vocabulary is clear.",'
                '"grammar_score":6.5,"grammar_feedback":"Uses simple and complex forms.",'
                '"pronunciation_score":null,"strengths":["Relevant examples"],'
                '"areas_for_improvement":["Vary linking phrases"],'
                '"suggested_expressions":[],"examiner_summary":"Clear response."}'
                '[/EVALUATION]'
            )

        if "IELTS Speaking Examiner" in prompt:
            return "Could you tell me a little more about that?"

        return (
            'That sounds interesting. What did you enjoy most?\n'
            '[CORRECTIONS]{"corrections":[{"original":"She don\'t",'
            '"corrected":"She doesn\'t","explanation":"Use does with she.",'
            '"category":"grammar","should_repeat":true}]}'
            '[/CORRECTIONS]'
        )

    async def chat_with_metadata(self, messages, options=None):
        return await self.chat(messages, options), {
            "provider_used": "test-stub",
            "model_used": "deterministic-test-model",
            "fallback_triggered": False,
            "latency_ms": 0.0,
        }


@pytest.fixture(autouse=True)
def stub_external_llm(monkeypatch):
    """API contract tests must pass even when Ollama/cloud providers are offline."""
    from app.api import conversation, ielts, progress

    router = StubModelRouter()
    monkeypatch.setattr(conversation, "get_model_router", lambda: router)
    monkeypatch.setattr(ielts, "get_model_router", lambda: router)
    monkeypatch.setattr(progress, "get_model_router", lambda: router)


def pytest_sessionfinish(session, exitstatus):
    """Remove only this run's temporary database after SQLAlchemy closes it."""
    try:
        from app.core.database import engine

        engine.dispose()
    except Exception:
        pass

    for suffix in ("", "-wal", "-shm"):
        Path(f"{TEST_DB_PATH}{suffix}").unlink(missing_ok=True)
