import asyncio
import sqlite3

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine, text

from tests.test_learning_foundation import client, identity, start
from app.core.database import SessionLocal, init_db
from app.models.learning import LearningEventModel, LearningAttemptModel
from app.schemas.learning import TutorRequest


def test_missing_corrupt_audio_and_traversal_fail_closed(client,monkeypatch,tmp_path):
    h=identity(client)
    monkeypatch.setattr('app.api.learning.CONTENT_DIR',tmp_path)
    url='/api/v1/learning/media/listening-change/0.2.0/example?preview=true'
    assert client.get(url,headers=h).status_code==503
    (tmp_path/'listening-020-example.wav').write_bytes(b'not a wave')
    assert client.get(url,headers=h).status_code==503
    assert client.get('/api/v1/learning/media/%2e%2e/%2e%2e/config.py',headers=h).status_code!=200


def test_cancelled_tutor_keeps_draft_and_no_feedback_event(client,monkeypatch):
    from app.api.learning import tutor
    h=identity(client);attempt=start(client,h)
    url='/api/v1/learning/attempts/'+attempt['id']
    assert client.patch(url,headers=h,json={'expected_revision':0,'step_id':'guided','draft':'Keep this draft'}).status_code==200
    async def check():
        entered=asyncio.Event()
        class Blocked:
            async def chat_with_metadata(self,*args,**kwargs):
                entered.set();await asyncio.Event().wait()
        monkeypatch.setattr('app.api.learning.get_model_router',lambda:Blocked())
        with SessionLocal() as db:
            row=db.get(LearningAttemptModel,attempt['id'])
            task=asyncio.create_task(tutor(row.id,TutorRequest(request_id='cancelled-request',step_id='guided',question='Explain'),(row.owner_user_id,row.profile_id),db))
            await asyncio.wait_for(entered.wait(),timeout=2);task.cancel()
            with pytest.raises(asyncio.CancelledError):await task
    asyncio.run(check())
    assert client.get(url,headers=h).json()['draft']=='Keep this draft'
    with SessionLocal() as db:assert db.query(LearningEventModel).filter_by(attempt_id=attempt['id']).count()==0


def test_old_sqlite_migration_is_idempotent_and_backup_restores(tmp_path,monkeypatch):
    old=tmp_path/'old.db';backup=tmp_path/'backup.db'
    with sqlite3.connect(old) as conn:
        conn.execute('CREATE TABLE sessions (id VARCHAR PRIMARY KEY, user_id VARCHAR, mode VARCHAR NOT NULL, started_at DATETIME, ended_at DATETIME, topic VARCHAR, total_speaking_ms INTEGER, estimated_band FLOAT, evaluation_json VARCHAR, provider VARCHAR)')
        conn.execute("INSERT INTO sessions (id,user_id,mode,topic) VALUES ('legacy','default','daily','Keep old history')")
        conn.commit()
        with sqlite3.connect(backup) as target:conn.backup(target)
    engine=create_engine('sqlite:///'+str(old))
    monkeypatch.setattr('app.core.database.engine',engine)
    monkeypatch.setattr('app.migrations.runner.engine',engine)
    init_db();init_db()
    with engine.connect() as conn:
        assert conn.execute(text("SELECT topic FROM sessions WHERE id='legacy'")).scalar()=='Keep old history'
        assert conn.execute(text("SELECT COUNT(*) FROM schema_migrations WHERE version='010_learning_review_policy'")).scalar()==1
    engine.dispose()
    restored=tmp_path/'restored.db'
    with sqlite3.connect(backup) as source,sqlite3.connect(restored) as target:source.backup(target)
    with sqlite3.connect(restored) as conn:assert conn.execute("SELECT topic FROM sessions WHERE id='legacy'").fetchone()[0]=='Keep old history'


def test_retired_version_resumes_only_for_its_existing_owner(client):
    from app.models.learning import LearningLessonModel
    h=identity(client);other=identity(client);start(client,h)
    with SessionLocal() as db:
        lesson=db.get(LearningLessonModel,('reading-change','0.1.0'))
        lesson.retired=True;db.commit()
        try:
            url='/api/v1/learning/lessons/reading-change?version=0.1.0'
            assert client.get(url,headers=h).status_code==200
            assert client.get(url,headers=other).status_code==404
            assert client.post('/api/v1/learning/attempts?preview=true',headers=h,json={
                'lesson_id':'reading-change','version':'0.1.0','request_id':'new-retired-attempt'}).status_code==404
        finally:
            lesson.retired=False;db.commit()


def test_review_export_and_profile_delete_preserve_other_profile(client):
    from tests.test_learning_slices import start as start_slice, submit
    from app.models.learning import LearningReviewModel, LearningObservationModel
    h=identity(client)
    keep=client.post('/api/v1/profiles',headers=h,json={'name':'Keep this profile'}).json()['id']
    url=start_slice(client,h,'reading')
    for n,answer in enumerate(['9','15','train','25'],1):submit(client,h,url,'independent',f'i{n}',answer)
    assert len(client.get('/api/v1/learning/export',headers=h).json()['reviews'])==1
    assert client.delete('/api/v1/profiles/'+h['X-Profile-Id'],headers=h).status_code==200
    with SessionLocal() as db:
        for model in (LearningReviewModel,LearningObservationModel,LearningAttemptModel,LearningEventModel):
            assert db.query(model).filter_by(profile_id=h['X-Profile-Id']).count()==0
    assert client.get('/api/v1/learning/units',headers={**h,'X-Profile-Id':keep}).status_code==200


def test_new_profile_has_no_invented_band_streak_or_speech_rate(client):
    h=identity(client)
    r=client.get('/api/v1/progress/summary',headers=h)
    assert r.status_code==200,r.text
    assert r.json()['latest_band'] is None and r.json()['streak']==0 and r.json()['avg_wpm']==0
