"""Unit tests for Whisper response types and optional runtime readiness."""

from app.services.stt.whisper_service import WhisperService


def test_speech_metrics_return_integer_millisecond_fields():
    service = WhisperService.__new__(WhisperService)
    metrics = service.calculate_metrics(
        segments=[{"start": 0.125, "end": 1.234}],
        text="I went there yesterday.",
        duration_ms=1234.6,
    )

    assert metrics["total_duration_ms"] == 1235
    assert metrics["speaking_duration_ms"] == 1109
    assert isinstance(metrics["total_duration_ms"], int)
    assert isinstance(metrics["speaking_duration_ms"], int)
