"""Speech readiness checks must not download Whisper weights on page load."""

from fastapi.testclient import TestClient

from app.main import app
from app.services.stt import whisper_service


def test_speech_status_reports_missing_dependency_without_loading_model(monkeypatch):
    def fail_if_model_loads(self):
        raise AssertionError("The status endpoint must not initialize WhisperModel")

    monkeypatch.setattr(whisper_service, "_whisper_service", None)
    monkeypatch.setattr(whisper_service.WhisperService, "__init__", fail_if_model_loads)
    monkeypatch.setattr(
        whisper_service.WhisperService,
        "package_installed",
        staticmethod(lambda: False),
    )

    with TestClient(app) as client:
        response = client.get("/api/v1/speech/status")

    assert response.status_code == 200, response.text
    assert response.json()["package_installed"] is False
    assert "faster-whisper" in response.json()["message"]
