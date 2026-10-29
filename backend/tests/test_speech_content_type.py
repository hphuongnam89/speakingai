import io
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_transcribe_accepts_webm_with_codecs_parameter():
    # Mock audio bytes
    fake_audio = io.BytesIO(b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88\x58\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00")
    files = {"audio": ("speech.webm", fake_audio, "audio/webm;codecs=opus")}
    data = {"session_id": "placement-test"}
    
    # We expect 200 or 503 (if whisper model is loading/failing on fake audio), but NOT 415 Unsupported Media Type!
    response = client.post("/api/v1/speech/transcribe", files=files, data=data)
    assert response.status_code != 415

def test_transcribe_rejects_unsupported_type():
    fake_file = io.BytesIO(b"fake data")
    files = {"audio": ("test.exe", fake_file, "application/x-msdownload")}
    data = {"session_id": "placement-test"}
    response = client.post("/api/v1/speech/transcribe", files=files, data=data)
    assert response.status_code == 415
