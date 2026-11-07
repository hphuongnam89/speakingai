import hashlib
import json
import sqlite3
import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.main import app
from app.core.database import Base, SessionLocal, init_db
from app.core.config import settings
from app.models.learning import LearningObservationModel
from app.schemas.learning import Lesson
from app.services.learning_content import CONTENT_DIR, read_pack, import_pack, learner_lesson


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def identity(client):
    response = client.post("/api/v1/auth/register", json={"email": uuid.uuid4().hex+"@test.invalid", "password": "test-password-123"})
    assert response.status_code == 201, response.text
    headers = {"Authorization": "Bearer "+response.json()["access_token"]}
    p = client.post("/api/v1/profiles", headers=headers, json={"name": "Learning test"})
    assert p.status_code == 200, p.text
    return {**headers, "X-Profile-Id": p.json()["id"]}


def start(client, headers, lesson="reading-change"):
    r = client.post("/api/v1/learning/attempts?preview=true", headers=headers,
        json={"lesson_id":lesson,"version":"0.1.0","request_id":uuid.uuid4().hex})
    assert r.status_code == 200, r.text
    return r.json()


def test_catalog_validates_and_never_implies_human_approval():
    lessons = read_pack()
    assert len(lessons) == 4
    assert {l.skill for l in lessons} == {"reading","listening","writing","speaking"}
    assert all(l.status == "draft" and l.provenance.reviewer_id is None for l in lessons)
    for lesson in lessons:
        payload = learner_lesson(lesson)
        for step in payload["steps"]:
            assert "hints" not in step
            assert all(set(item) == {"id","prompt"} for item in step["items"])


def test_content_cannot_be_released_without_review():
    value = read_pack()[0].model_dump()
    value["status"] = "published"
    with pytest.raises(ValidationError):
        Lesson.model_validate(value)


def test_content_checksum_paths_cycles_and_immutable_version(tmp_path):
    value = read_pack()[0].model_dump()
    value["prerequisites"] = [value["competency_id"]]
    raw = json.dumps(value).encode()
    (tmp_path/"lesson.json").write_bytes(raw)
    manifest = {"competencies":[value["competency_id"]], "lessons":[{"file":"lesson.json","sha256":hashlib.sha256(raw).hexdigest()}]}
    (tmp_path/"manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="Cyclic"):
        read_pack(tmp_path)
    manifest["lessons"][0]["file"]="../outside.json"
    (tmp_path/"manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="path"):
        read_pack(tmp_path)
    manifest["lessons"][0]["file"]="lesson.json"
    manifest["lessons"][0]["sha256"]="bad"
    (tmp_path/"manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="Checksum"):
        read_pack(tmp_path)
    init_db()
    with SessionLocal() as db:
        import_pack(db)
        assert import_pack(db)["validated"] == 4
        from app.models.learning import LearningLessonModel
        row=db.get(LearningLessonModel,("reading-change","0.1.0"))
        original=row.checksum
        row.checksum="tampered";db.commit()
        try:
            with pytest.raises(ValueError,match="immutable"):
                import_pack(db)
        finally:
            db.rollback();row.checksum=original;db.commit()


def test_learning_requires_login_and_owned_profile(client):
    assert client.get("/api/v1/learning/units").status_code == 401
    a, b = identity(client), identity(client)
    row = start(client,a)
    assert client.get("/api/v1/learning/attempts/"+row["id"],headers=b).status_code == 404
    assert client.get("/api/v1/learning/units",headers={**a,"X-Profile-Id":b["X-Profile-Id"]}).status_code == 404
    assert client.get("/api/v1/sessions",headers={**a,"X-Profile-Id":"not-a-profile"}).status_code == 404


def test_preview_not_published_and_production_cannot_preview(client, monkeypatch):
    h = identity(client)
    assert client.get("/api/v1/learning/units",headers=h).json()["lessons"] == []
    assert len(client.get("/api/v1/learning/units?preview=true",headers=h).json()["lessons"]) == 4
    monkeypatch.setattr(settings,"ENVIRONMENT","production")
    assert client.get("/api/v1/learning/units?preview=true",headers=h).json()["lessons"] == []
    assert client.get("/api/v1/learning/lessons/reading-change?version=0.1.0&preview=true",headers=h).status_code == 404


def test_draft_resume_conflict_and_strict_input(client):
    h = identity(client)
    a = start(client,h)
    url = "/api/v1/learning/attempts/"+a["id"]
    body={"step_id":"guided","draft":"my own words","expected_revision":0}
    assert client.patch(url,headers=h,json=body).status_code == 200
    assert client.patch(url,headers=h,json=body).status_code == 409
    assert client.get(url,headers=h).json()["draft"] == "my own words"
    assert client.patch(url,headers=h,json={"step_id":"transfer","draft":"new context","expected_revision":1}).status_code == 200
    assert client.get(url,headers=h).json()["drafts"] == {"guided":"my own words","transfer":"new context"}
    assert client.patch(url,headers=h,json={**body,"owner_user_id":"other"}).status_code == 422
    assert client.patch(url,headers=h,json={**body,"draft":"x"*12001}).status_code == 422


def test_hint_retry_is_idempotent_and_submission_is_assisted(client):
    h=identity(client);a=start(client,h);base="/api/v1/learning/attempts/"+a["id"]
    hint={"step_id":"independent","request_id":"hint-retry-test"}
    first=client.post(base+"/hints",headers=h,json=hint)
    assert first.status_code == 200,first.text
    assert client.post(base+"/hints",headers=h,json=hint).json() == first.json()
    body={"step_id":"independent","item_id":"i1","text":"9","request_id":"answer-retry-test"}
    r=client.post(base+"/submit",headers=h,json=body)
    assert r.status_code == 200,r.text
    assert r.json()["result"] == "met" and r.json()["evidence_kind"] == "assisted"
    assert client.post(base+"/submit",headers=h,json=body).json() == r.json()
    assert client.post(base+"/submit",headers=h,json={**body,"text":"8"}).status_code == 409
    with SessionLocal() as db:
        assert db.query(LearningObservationModel).filter_by(attempt_id=a["id"]).count() == 1


def test_new_item_is_independent_but_repeated_item_is_not(client):
    h=identity(client);a=start(client,h);url="/api/v1/learning/attempts/"+a["id"]+"/submit"
    def submit(item,answer):
        return client.post(url,headers=h,json={"step_id":"independent","item_id":item,"text":answer,"request_id":uuid.uuid4().hex}).json()
    assert submit("i1","9")["evidence_kind"] == "independent"
    assert submit("i2","15")["evidence_kind"] == "independent"
    assert submit("i1","9")["evidence_kind"] == "assisted"


def test_review_and_today_are_owner_scoped(client):
    h = identity(client)
    a = start(client, h)
    response = client.post("/api/v1/learning/attempts/"+a["id"]+"/submit", headers=h,
        json={"step_id":"independent","item_id":"i1","text":"9","request_id":uuid.uuid4().hex})
    assert response.status_code == 200 and response.json()["evidence_kind"] == "independent"
    reviews = client.get("/api/v1/learning/reviews", headers=h)
    assert reviews.status_code == 200 and reviews.json()["reviews"] == []
    today = client.get("/api/v1/learning/today?preview=true", headers=h)
    assert today.status_code == 200 and today.json()["recommendations"]
    other = identity(client)
    assert client.get("/api/v1/learning/reviews", headers=other).json()["reviews"] == []


def test_reading_evidence_is_checked_without_exposing_the_key(client):
    h = identity(client)
    a = start(client, h)
    response = client.post("/api/v1/learning/attempts/"+a["id"]+"/submit", headers=h,
        json={"step_id":"independent","item_id":"i1","text":"9",
              "evidence":"The library usually opens at 8. Today's opening time is 9.","request_id":uuid.uuid4().hex})
    assert response.status_code == 200 and response.json()["result"] == "met"
    assert response.json()["evidence_match"] is True


def test_productive_answer_is_not_given_a_fake_band(client):
    h=identity(client);a=start(client,h,"writing-change")
    r=client.post("/api/v1/learning/attempts/"+a["id"]+"/submit",headers=h,json={"step_id":"independent","item_id":"i1","text":"Could we meet on Saturday? I have a class on Friday.","request_id":uuid.uuid4().hex})
    assert r.json()["result"] == "unknown" and r.json()["assessment_band"] is None
    assert client.get("/api/v1/learning/reviews", headers=h).json()["reviews"] == []


def test_tutor_uses_teaching_sources_and_validates_output(client,monkeypatch):
    h=identity(client);a=start(client,h)
    class Tutor:
        async def chat_with_metadata(self,messages,options):
            data=json.loads(messages[1]["content"])
            assert {s["id"] for s in data["sources"]} == {"explain","example","guided"}
            assert "library" not in messages[1]["content"]
            assert options["local_only"] and not options["cloud_fallback"]
            return json.dumps({"claim_type":"explanation","explanation":"Đọc cả câu để xác định lịch mới.","next_action":"Hãy giải thích thông tin nào còn hiệu lực.","source_step_id":"example"}),{"provider_used":"test-stub"}
    monkeypatch.setattr("app.api.learning.get_model_router",lambda:Tutor())
    url="/api/v1/learning/attempts/"+a["id"]+"/tutor"
    body={"step_id":"guided","question":"Tôi cần chú ý điều gì?","request_id":uuid.uuid4().hex}
    response=client.post(url,headers=h,json=body)
    assert response.status_code == 200,response.text
    assert client.post(url,headers=h,json=body).json() == response.json()
    assert client.post(url,headers=h,json={**body,"request_id":uuid.uuid4().hex,"step_id":"transfer"}).status_code == 409
    class Malformed:
        async def chat_with_metadata(self,*args):return "not JSON",{}
    monkeypatch.setattr("app.api.learning.get_model_router",lambda:Malformed())
    assert client.post(url,headers=h,json={**body,"request_id":uuid.uuid4().hex}).status_code == 502
    class InventedSource:
        async def chat_with_metadata(self,*args):
            return json.dumps({"claim_type":"explanation","explanation":"Unsupported claim","next_action":"Try again","source_step_id":"transfer-secret-key"}),{}
    monkeypatch.setattr("app.api.learning.get_model_router",lambda:InventedSource())
    assert client.post(url,headers=h,json={**body,"request_id":uuid.uuid4().hex}).status_code == 502


def test_export_and_profile_delete_cover_learning_data(client):
    h=identity(client);a=start(client,h)
    assert len(client.get("/api/v1/learning/export",headers=h).json()["attempts"]) == 1
    client.post("/api/v1/profiles",headers=h,json={"name":"Keep this profile"})
    response=client.delete("/api/v1/profiles/"+h["X-Profile-Id"],headers=h)
    assert response.status_code == 200,response.text
    with SessionLocal() as db:
        from app.models.learning import LearningAttemptModel
        assert db.get(LearningAttemptModel,a["id"]) is None


def test_browser_cookie_auth_origin_and_logout(client):
    email=uuid.uuid4().hex+"@test.invalid"
    headers={"Origin":"http://testserver","X-Browser-Session":"true"}
    r=client.post("/api/v1/auth/register",headers=headers,json={"email":email,"password":"test-password-123"})
    assert r.status_code == 201,r.text
    cookie=r.headers["set-cookie"].lower()
    assert "httponly" in cookie and "samesite=strict" in cookie
    assert client.get("/api/v1/auth/session").status_code == 200
    assert client.post("/api/v1/profiles",headers={"Origin":"https://attacker.invalid"},json={"name":"No"}).status_code == 403
    assert client.post("/api/v1/profiles",headers={"Origin":"http://testserver"},json={"name":"Browser"}).status_code == 200
    assert client.post("/api/v1/auth/logout",headers={"Origin":"http://testserver"}).status_code == 200
    assert client.get("/api/v1/auth/session").status_code == 401
    client.cookies.set("learning_session","expired")
    assert client.get("/api/v1/auth/session").status_code == 401
    client.cookies.clear()


def test_browser_origin_is_checked_before_creating_account(client):
    credentials={"email":uuid.uuid4().hex+"@test.invalid","password":"test-password-123"}
    assert client.post("/api/v1/auth/register",headers={"X-Browser-Session":"true","Origin":"https://attacker.invalid"},json=credentials).status_code == 403
    assert client.post("/api/v1/auth/login",json=credentials).status_code == 401


def test_model_selection_is_profile_scoped_and_never_downloads(client,monkeypatch):
    a,b=identity(client),identity(client)
    class Local:
        async def test_connection(self):return {"installed_models":["existing-model"]}
    class Router:
        ollama=Local()
        async def get_active_provider(self):return "ollama"
        async def get_available_models(self):return {"available":[],"active":"ollama"}
    monkeypatch.setattr("app.api.models.get_model_router",lambda:Router())
    original=settings.OLLAMA_MODEL
    assert client.post("/api/v1/models/select",headers=a,json={"model":"missing"}).status_code == 422
    assert client.post("/api/v1/models/select",headers=a,json={"model":"existing-model"}).status_code == 200
    assert client.get("/api/v1/models",headers=a).json()["selected_model"] == "existing-model"
    assert client.get("/api/v1/models",headers=b).json()["selected_model"] == original
    assert settings.OLLAMA_MODEL == original


def test_concurrent_submit_does_not_duplicate_evidence(client):
    from concurrent.futures import ThreadPoolExecutor
    h=identity(client);a=start(client,h);url="/api/v1/learning/attempts/"+a["id"]+"/submit"
    body={"step_id":"independent","item_id":"i1","text":"9","request_id":uuid.uuid4().hex}
    with ThreadPoolExecutor(max_workers=2) as pool:
        responses=list(pool.map(lambda _:client.post(url,headers=h,json=body),range(2)))
    assert all(r.status_code in {200,409} for r in responses)
    assert client.post(url,headers=h,json=body).status_code == 200
    with SessionLocal() as db:
        assert db.query(LearningObservationModel).filter_by(attempt_id=a["id"]).count() == 1


def test_additive_learning_tables_and_backup_restore_old_history(tmp_path):
    source=tmp_path/"old.db";backup=tmp_path/"backup.db"
    with sqlite3.connect(source) as connection:
        connection.execute("CREATE TABLE legacy_history (id TEXT, transcript TEXT)")
        connection.execute("INSERT INTO legacy_history VALUES ('old','Keep my speaking history')")
        connection.commit()
        with sqlite3.connect(backup) as destination:connection.backup(destination)
    engine=create_engine("sqlite:///"+str(source))
    Base.metadata.create_all(engine)
    Base.metadata.create_all(engine)
    with engine.connect() as db:
        assert db.execute(text("SELECT transcript FROM legacy_history")).scalar() == "Keep my speaking history"
        assert db.execute(text("SELECT count(*) FROM learning_attempts")).scalar() == 0
    with sqlite3.connect(backup) as saved:
        assert saved.execute("SELECT transcript FROM legacy_history").fetchone()[0] == "Keep my speaking history"
    engine.dispose()
