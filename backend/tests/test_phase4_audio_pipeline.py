import io
from fastapi.testclient import TestClient
from app.main import app
from app.services.pronunciation.pronunciation_service import PronunciationService
from app.services.stt.whisper_service import WhisperService

client = TestClient(app)


def test_pronunciation_boundary_confidence_vs_score():
    service = PronunciationService()
    test_text = "I really enjoy studying computer science and software development."
    mock_words = [
        {"word": "i", "start": 0.0, "end": 0.2, "probability": 0.98},
        {"word": "really", "start": 0.25, "end": 0.6, "probability": 0.95},
        {"word": "enjoy", "start": 0.65, "end": 1.0, "probability": 0.92},
        {"word": "studying", "start": 1.1, "end": 1.5, "probability": 0.88},
        {"word": "computer", "start": 1.6, "end": 2.1, "probability": 0.91},
        {"word": "science", "start": 2.15, "end": 2.6, "probability": 0.89},
        {"word": "and", "start": 2.65, "end": 2.8, "probability": 0.99},
        {"word": "software", "start": 2.85, "end": 3.3, "probability": 0.75},  # Low confidence (<0.80)
        {"word": "development", "start": 3.35, "end": 4.0, "probability": 0.94},
    ]

    report = service.analyze_speech(
        text=test_text,
        words_data=mock_words,
        duration_ms=4500.0
    )

    # 1. Recognition confidence is present and calculated from Whisper probabilities
    assert report.recognition_confidence is not None
    assert 0.0 <= report.recognition_confidence <= 100.0

    # 2. Crucial boundary: pronunciation_score MUST be None when no acoustic assessor is active
    assert report.pronunciation_score is None

    # 3. Disclaimer must explicitly state that Whisper confidence is NOT a pronunciation score
    assert "not a pronunciation score" in report.feedback_summary.lower()
    assert "whisper confidence is not pronunciation accuracy" in report.disclaimer.lower()

    # 4. Low-confidence word is flagged for transcript review, not falsely marked as mispronounced
    assert any(w.word.lower() == "software" and w.needs_review for w in report.words)


def test_audio_metrics_calculation():
    service = WhisperService.__new__(WhisperService)
    segments = [
        {"start": 0.0, "end": 2.0, "text": "Um I think that uh learning languages is beneficial."},
        {"start": 4.0, "end": 7.0, "text": "Because it opens many new career opportunities like you know."}
    ]
    full_text = "Um I think that uh learning languages is beneficial. Because it opens many new career opportunities like you know."
    total_duration_ms = 7500.0

    metrics = service.calculate_metrics(segments, full_text, total_duration_ms)

    assert metrics["total_duration_ms"] == 7500
    # Speaking duration is (2-0) + (7-4) = 5.0 seconds = 5000 ms
    assert metrics["speaking_duration_ms"] == 5000
    # Long pause between 2.0 and 4.0 is 2.0s (> 1.5s) -> 1 long pause
    assert metrics["long_pauses"] == 1
    # Fillers counted: 'um', 'uh', 'like', 'you know' -> at least 4 fillers
    assert metrics["filler_count"] >= 4
    # WPM must be positive and reasonable
    assert metrics["wpm"] > 0


def test_audio_upload_unsupported_content_type_rejected():
    fake_audio = io.BytesIO(b"fake text content")
    response = client.post(
        "/api/v1/speech/transcribe",
        data={"session_id": "test-session"},
        files={"audio": ("test.txt", fake_audio, "text/plain")}
    )
    assert response.status_code == 415
    assert "unsupported" in response.json()["detail"].lower()


def test_audio_upload_invalid_session_rejected():
    fake_audio = io.BytesIO(b"\x00\x01\x02\x03")
    response = client.post(
        "/api/v1/speech/transcribe",
        data={"session_id": "invalid session with spaces and *&^%"},
        files={"audio": ("test.wav", fake_audio, "audio/wav")}
    )
    assert response.status_code == 400
    assert "invalid session_id" in response.json()["detail"].lower()
