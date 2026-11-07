import json
import uuid
from types import SimpleNamespace

import pytest

from tests.test_learning_foundation import client, identity
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.session import SessionModel
from app.models.turn import TurnModel
from app.models.progress import DailyStatsModel
from app.prompts.ielts import parse_evaluation
from app.services.assessment import report, VERSION


@pytest.mark.parametrize('raw', ['not json', '{}', '[]', '{"lexical_score":NaN,"grammar_score":6}',
    '{"lexical_score":99,"grammar_score":6}', '{"lexical_score":true,"grammar_score":6}',
    '{"lexical_score":6,"grammar_score":6,"strengths":"invented"}',
    '{"lexical_score":6,"grammar_score":6,"suggested_expressions":[{}]}',
    '{"lexical_score":'+('9'*400)+',"grammar_score":6}', '['*1500+']'*1500])
def test_malformed_or_unsupported_model_data_abstains(raw):
    result=parse_evaluation(raw)
    assert result['overall_band'] is None and result['lexical_score'] is None
    assert result['confidence'] is None and not result['strengths']


def session(client,h,text):
    r=client.post('/api/v1/ielts/start',headers=h,json={'part':'part1'})
    assert r.status_code==200,r.text
    sid=r.json()['session_id']
    with SessionLocal() as db:
        row=db.get(SessionModel,sid)
        db.add(TurnModel(session_id=sid,owner_user_id=row.owner_user_id,role='user',transcript=text))
        db.commit()
    return sid


def test_short_input_does_not_invent_grade_finish_or_call_model(client,monkeypatch):
    h=identity(client);sid=session(client,h,'Hello there.')
    monkeypatch.setattr('app.api.ielts.get_model_router',lambda:pytest.fail('Short input must not call model'))
    r=client.post('/api/v1/ielts/evaluate/'+sid,headers=h)
    assert r.status_code==200,r.text
    assert r.json()['score_status']=='insufficient_evidence' and r.json()['overall_band'] is None
    with SessionLocal() as db:
        row=db.get(SessionModel,sid)
        assert row.evaluation_json is None and row.ended_at is None


def test_assessment_tracks_actual_model_and_never_infers_audio_or_time(client):
    h=identity(client);sid=session(client,h,'I enjoy learning English with friends because we can discuss ideas and help each other. '*4)
    first=client.post('/api/v1/ielts/evaluate/'+sid,headers=h)
    assert first.status_code==200,first.text
    result=first.json()
    assert result['score_status']=='provisional' and result['lexical_score']==6.0
    assert result['model_id']=='deterministic-test-model' and result['provider']=='test-stub'
    assert all(result[k] is None for k in ('overall_band','fluency_score','pronunciation_score','confidence'))
    assert '±' not in result['confidence_range'] and result['scoring_version']==VERSION
    assert client.post('/api/v1/ielts/evaluate/'+sid,headers=h).json()==result
    with SessionLocal() as db:
        assert db.get(SessionModel,sid).total_speaking_ms==0
        stats=db.query(DailyStatsModel).filter_by(user_id=h['X-Profile-Id']).all()
        assert sum(s.speaking_minutes for s in stats)==0


def test_legacy_report_is_preserved_but_not_mislabelled(client):
    h=identity(client);sid=session(client,h,'This is a short practice answer.')
    original=json.dumps({'overall_band':6,'score_status':'calibrated','confidence':.95})
    with SessionLocal() as db:
        db.get(SessionModel,sid).evaluation_json=original;db.commit()
    r=client.post('/api/v1/ielts/evaluate/'+sid,headers=h)
    assert r.status_code==200 and r.json()['overall_band'] is None
    with SessionLocal() as db:assert db.get(SessionModel,sid).evaluation_json==original


def test_malformed_report_can_retry_without_poisoning_cache(client,monkeypatch):
    h=identity(client);sid=session(client,h,'I enjoy learning English with friends because we can discuss ideas and help each other. '*4)
    class Bad:
        async def chat_with_metadata(self,*args,**kwargs):return 'broken',{'model_used':'test','provider_used':'test'}
    monkeypatch.setattr('app.api.ielts.get_model_router',lambda:Bad())
    r=client.post('/api/v1/ielts/evaluate/'+sid,headers=h)
    assert r.status_code==200 and r.json()['score_status']=='unavailable'
    with SessionLocal() as db:assert db.get(SessionModel,sid).evaluation_json is None


def test_calibration_admin_consent_idempotency_and_no_fake_readiness(client,monkeypatch):
    h=identity(client);monkeypatch.setattr(settings,'CALIBRATION_ADMIN_KEY','test-admin-key')
    body={'sample_key':uuid.uuid4().hex,'transcript':'QA synthetic text','human_fc':6,'consented':True}
    url='/api/v1/ielts/calibration/samples'
    assert client.post(url,headers=h,json=body).status_code==403
    assert client.get('/api/v1/ielts/calibration/status',headers=h).status_code==403
    admin={**h,'X-Calibration-Key':'test-admin-key'}
    assert client.post(url,headers=admin,json={**body,'consented':False}).status_code==422
    assert client.post(url,headers=admin,json={**body,'human_fc':99}).status_code==422
    assert client.post(url,headers=admin,json=body).status_code==200
    assert client.post(url,headers=admin,json=body).status_code==200
    assert client.post(url,headers=admin,json={**body,'transcript':'different'}).status_code==409
    assert client.get('/api/v1/ielts/calibration/status',headers=admin).json()['ready'] is False


def test_unknown_model_provenance_abstains():
    payload=parse_evaluation('{"lexical_score":6,"grammar_score":6}')
    turns=[SimpleNamespace(role='user',transcript='word '*50)]
    assert report(payload,turns,{})['score_status']=='unavailable'


def test_concurrent_evaluation_counts_one_activity(client):
    from concurrent.futures import ThreadPoolExecutor
    h=identity(client);sid=session(client,h,'I enjoy learning English with friends because we can discuss ideas and help each other. '*4)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(lambda _:client.post('/api/v1/ielts/evaluate/'+sid,headers=h),range(2)))
    assert all(r.status_code==200 for r in results)
    with SessionLocal() as db:
        stats=db.query(DailyStatsModel).filter_by(user_id=h['X-Profile-Id']).all()
        assert sum(s.session_count for s in stats)==1


def test_assessment_request_limits_and_ownership(client):
    h=identity(client);sid=session(client,h,'Hello there.')
    other=identity(client)
    assert client.post('/api/v1/ielts/evaluate/'+sid,headers=other).status_code==404
    assert client.post('/api/v1/ielts/respond',headers=h,json={'session_id':sid,'user_text':'x'*12001}).status_code==422
    assert client.post('/api/v1/ielts/start',headers=h,json={'topic':'x'*2001}).status_code==422
    assert parse_evaluation('x'*30001)['score_status']=='unavailable'


def test_placement_never_invents_band_from_invalid_or_text_only_output(client,monkeypatch):
    h=identity(client);profile=h['X-Profile-Id']
    body={'profile_id':profile,'answers':[{'question_id':i,'question':'injected user question',
        'answer':'I enjoy learning English with friends because we discuss interesting ideas together every single day.'} for i in range(1,4)]}
    class Provider:
        raw='malformed JSON'
        async def chat_with_metadata(self,messages,options):
            assert 'injected user question' not in messages[1]['content'] and options['local_only']
            return self.raw,{'provider_used':'test','model_used':'model-test'}
    provider=Provider()
    monkeypatch.setattr('app.api.placement.get_model_router',lambda:provider)
    url='/api/v1/placement/evaluate'
    assert client.post(url,headers=h,json=body).status_code==502
    assert client.get('/api/v1/profiles',headers=h).json()[0]['placement_status']!='completed'
    provider.raw=json.dumps({'estimated_band':8,'pronunciation_score':9,'lexical_score':6,'grammar_score':6.5,
                             'examiner_verdict':'Text-based feedback only', 'roadmap':{'phases':[]}})
    r=client.post(url,headers=h,json=body)
    assert r.status_code==200,r.text
    assert r.json()['estimated_band'] is None and r.json()['pronunciation_score'] is None
    assert r.json()['lexical_score']==6 and r.json()['calibration_status']=='unverified'
    assert client.get('/api/v1/profiles',headers=h).json()[0]['current_band'] is None
