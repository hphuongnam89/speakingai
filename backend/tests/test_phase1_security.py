from pathlib import Path

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.audio import AudioRecordingModel
from app.models.session import SessionModel
from app.models.mistake import MistakeModel

client = TestClient(app)


def test_profile_isolation_between_authenticated_users():
    a = client.post("/api/v1/auth/register", json={"email": "phase1-a@example.com", "password": "a-secure-password-123"})
    b = client.post("/api/v1/auth/register", json={"email": "phase1-b@example.com", "password": "b-secure-password-123"})
    assert a.status_code == 201 and b.status_code == 201
    token_a = a.json()["access_token"]
    token_b = b.json()["access_token"]
    profile_a = client.post("/api/v1/profiles", headers={"Authorization": f"Bearer {token_a}"}, json={"name": "A"}).json()
    profile_b = client.post("/api/v1/profiles", headers={"Authorization": f"Bearer {token_b}"}, json={"name": "B"}).json()
    denied = client.get(f"/api/v1/profiles/{profile_b['id']}", headers={"Authorization": f"Bearer {token_a}"})
    assert denied.status_code == 404
    assert client.get(f"/api/v1/profiles/{profile_a['id']}", headers={"Authorization": f"Bearer {token_a}"}).status_code == 200


def test_reset_all_removes_owned_audio_file(tmp_path: Path):
    audio = tmp_path / "owned.wav"
    audio.write_bytes(b"test-audio")
    with SessionLocal() as db:
        db.add(AudioRecordingModel(owner_user_id="default", file_path=str(audio), content_type="audio/wav", size_bytes=10))
        db.commit()
    response = client.post("/api/v1/profiles/reset-all")
    assert response.status_code == 200
    assert not audio.exists()


def test_delete_profile_removes_associated_audio_files(tmp_path: Path):
    u = client.post("/api/v1/auth/register", json={"email": "del-profile@example.com", "password": "secure-pwd-12345"})
    assert u.status_code == 201
    token = u.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create 2 profiles (so one can be deleted)
    p1 = client.post("/api/v1/profiles", headers=headers, json={"name": "P1"}).json()
    p2 = client.post("/api/v1/profiles", headers=headers, json={"name": "P2"}).json()

    # Create a session and an audio recording for p1
    audio_file = tmp_path / "p1_recording.wav"
    audio_file.write_bytes(b"profile-1-audio-bytes")

    with SessionLocal() as db:
        sess = SessionModel(user_id=p1["id"], owner_user_id=u.json()["user_id"], mode="daily")
        db.add(sess)
        db.commit()
        db.refresh(sess)
        db.add(AudioRecordingModel(
            owner_user_id=u.json()["user_id"],
            session_id=sess.id,
            file_path=str(audio_file),
            content_type="audio/wav",
            size_bytes=21
        ))
        db.commit()

    assert audio_file.exists()
    del_resp = client.delete(f"/api/v1/profiles/{p1['id']}", headers=headers)
    assert del_resp.status_code == 200
    # Audio file on disk must be cleaned up
    assert not audio_file.exists()


def test_session_idor_isolation():
    u1 = client.post("/api/v1/auth/register", json={"email": "idor-sess-1@example.com", "password": "password-123456"})
    u2 = client.post("/api/v1/auth/register", json={"email": "idor-sess-2@example.com", "password": "password-123456"})
    assert u1.status_code == 201 and u2.status_code == 201
    t1 = u1.json()["access_token"]
    t2 = u2.json()["access_token"]

    p1 = client.post("/api/v1/profiles", headers={"Authorization": f"Bearer {t1}"}, json={"name": "User 1"}).json()

    # User 1 creates a session
    sess = client.post("/api/v1/sessions", headers={"Authorization": f"Bearer {t1}", "X-Profile-Id": p1["id"]}, json={"mode": "daily"}).json()
    session_id = sess["id"]

    # User 1 can access it
    ok_resp = client.get(f"/api/v1/sessions/{session_id}", headers={"Authorization": f"Bearer {t1}", "X-Profile-Id": p1["id"]})
    assert ok_resp.status_code == 200

    # User 2 tries to access User 1's session -> must be 404 Not Found (IDOR protected)
    idor_get = client.get(f"/api/v1/sessions/{session_id}", headers={"Authorization": f"Bearer {t2}"})
    assert idor_get.status_code == 404

    # User 2 tries to finish User 1's session -> must be 404
    idor_finish = client.post(f"/api/v1/sessions/{session_id}/finish", headers={"Authorization": f"Bearer {t2}"})
    assert idor_finish.status_code == 404


def test_mistakes_idor_isolation():
    u1 = client.post("/api/v1/auth/register", json={"email": "idor-mis-1@example.com", "password": "password-123456"})
    u2 = client.post("/api/v1/auth/register", json={"email": "idor-mis-2@example.com", "password": "password-123456"})
    t1 = u1.json()["access_token"]
    t2 = u2.json()["access_token"]

    p1 = client.post("/api/v1/profiles", headers={"Authorization": f"Bearer {t1}"}, json={"name": "User 1"}).json()

    # Insert a mistake for user 1
    with SessionLocal() as db:
        m = MistakeModel(
            user_id=p1["id"],
            owner_user_id=u1.json()["user_id"],
            original_text="He go to school",
            corrected_text="He goes to school",
            category="grammar"
        )
        db.add(m)
        db.commit()
        db.refresh(m)
        mistake_id = m.id

    # User 1 sees the mistake
    resp1 = client.get("/api/v1/mistakes", headers={"Authorization": f"Bearer {t1}", "X-Profile-Id": p1["id"]})
    assert resp1.status_code == 200
    assert any(item["id"] == mistake_id for item in resp1.json())

    # User 2 does NOT see User 1's mistake
    resp2 = client.get("/api/v1/mistakes", headers={"Authorization": f"Bearer {t2}"})
    assert resp2.status_code == 200
    assert not any(item["id"] == mistake_id for item in resp2.json())

    # User 2 cannot resolve User 1's mistake
    resolve_resp = client.post(f"/api/v1/mistakes/{mistake_id}/resolve", headers={"Authorization": f"Bearer {t2}"})
    assert resolve_resp.status_code == 404

