import json
import uuid
from datetime import datetime, timedelta, timezone

from tests.test_learning_foundation import client, identity
from app.core.database import SessionLocal
from app.models.learning import LearningReviewModel
from app.services.learning_progress import competency_state


def start(client, headers, skill):
    r = client.post('/api/v1/learning/attempts?preview=true', headers=headers, json={
        'lesson_id':skill+'-change','version':'0.2.0','request_id':uuid.uuid4().hex})
    assert r.status_code == 200, r.text
    return '/api/v1/learning/attempts/'+r.json()['id']


def submit(client,h,url,step,item,text):
    r = client.post(url+'/submit',headers=h,json={'step_id':step,'item_id':item,'text':text,'request_id':uuid.uuid4().hex})
    assert r.status_code == 200,r.text
    return r.json()


def test_audio_range_auth_transcript_exposure(client):
    h=identity(client);url=start(client,h,'listening')
    lesson=client.get('/api/v1/learning/lessons/listening-change?version=0.2.0&preview=true',headers=h).json()
    step=next(s for s in lesson['steps'] if s['kind']=='independent')
    assert step['stimulus']=='' and all('answer' not in i for i in step['items'])
    media=step['audio_url']+'?preview=true'
    assert client.get(media).status_code==401
    audio=client.get(media,headers={**h,'Range':'bytes=0-43'})
    assert audio.status_code==206 and audio.content[:4]==b'RIFF'
    body={'step_id':'independent','kind':'transcript','request_id':uuid.uuid4().hex}
    response=client.post(url+'/exposure',headers=h,json=body)
    assert response.status_code==200 and 'table five' in response.json()['transcript']
    assert client.post(url+'/exposure',headers=h,json=body).json()==response.json()
    answer=submit(client,h,url,'independent','i1','5')
    assert answer['result']=='met' and answer['evidence_kind']=='assisted'


def test_review_policy_new_items_due_boundaries_and_exhaustion(client):
    h=identity(client);url=start(client,h,'reading')
    for i,answer in enumerate(['9','15','train','25'],1):
        submit(client,h,url,'independent',f'i{i}',answer)
    reviews=client.get('/api/v1/learning/reviews',headers=h).json()['reviews']
    assert len(reviews)==1 and reviews[0]['state']=='provisionally_mastered'
    body={'step_id':'review','item_id':'r1','text':'Wednesday','request_id':uuid.uuid4().hex}
    assert client.post(url+'/submit',headers=h,json=body).status_code==409
    other=identity(client)
    assert client.post('/api/v1/learning/reviews/'+reviews[0]['id']+'/reschedule',headers=other,json={'days':1}).status_code==404
    for item,answer in [('r1','Wednesday'),('r2','inside')]:
        with SessionLocal() as db:
            db.get(LearningReviewModel,reviews[0]['id']).next_review_at=datetime.now(timezone.utc)-timedelta(seconds=1);db.commit()
        plan=client.get('/api/v1/learning/today?preview=true',headers=h).json()
        assert any(r.get('item_id')==item for r in plan['recommendations'])
        assert submit(client,h,url,'review' if item=='r1' else 'review7',item,answer)['evidence_kind']=='retention'
    with SessionLocal() as db:
        db.get(LearningReviewModel,reviews[0]['id']).next_review_at=datetime.now(timezone.utc)-timedelta(seconds=1);db.commit()
    assert any('hết câu' in b['reason'] for b in client.get('/api/v1/learning/today?preview=true',headers=h).json()['blockers'])


def test_productive_feedback_preserves_unicode_and_draft_on_failure(client,monkeypatch):
    h=identity(client);url=start(client,h,'writing')
    original='🙂 Could we meet tomorrow?'
    submit(client,h,url,'independent','i1',original)
    class Feedback:
        async def chat_with_metadata(self,messages,options):
            assert options['local_only'] and not options['cloud_fallback']
            return json.dumps({'claim_type':'valid_alternative','explanation':'Lý do liên quan.','next_action':'Tự viết một đề xuất khác.',
                'source_step_id':'example','criteria':['Đề xuất rõ.'], 'annotations':[{'start':20,'end':50,'quote':'Could','comment':'Đề nghị lịch sự.'}]}),{}
    monkeypatch.setattr('app.api.learning.get_model_router',lambda:Feedback())
    body={'step_id':'independent','item_id':'i1','request_id':uuid.uuid4().hex}
    response=client.post(url+'/feedback',headers=h,json=body)
    assert response.status_code==200,response.text
    assert response.json()['assessment_band'] is None
    assert response.json()['annotations'][0]['start']==2
    assert client.post(url+'/feedback',headers=h,json=body).json()==response.json()
    class Bad:
        async def chat_with_metadata(self,*args):return '{}',{}
    monkeypatch.setattr('app.api.learning.get_model_router',lambda:Bad())
    assert client.post(url+'/feedback',headers=h,json={**body,'request_id':uuid.uuid4().hex}).status_code==502
    assert original in str(client.get(url,headers=h).json())


def test_speaking_bridge_is_idempotent_and_owner_scoped(client):
    h=identity(client);url=start(client,h,'speaking')
    a=client.post(url+'/speaking-session',headers=h)
    assert a.status_code==200
    assert client.post(url+'/speaking-session',headers=h).json()==a.json()
    assert client.post(url+'/speaking-session',headers=identity(client)).status_code==404
    assert client.post(url+'/submit',headers=h,json={'step_id':'independent','item_id':'i1','text':'My idea','turn_id':'someone-elses-turn','request_id':uuid.uuid4().hex}).status_code==422


def test_explicit_reason_is_not_falsely_reported_missing(client):
    h=identity(client);url=start(client,h,'writing')
    submit(client,h,url,'independent','i1','I cannot meet because I have a class. Could we meet tomorrow?')
    r=client.post(url+'/feedback',headers=h,json={'step_id':'independent','item_id':'i1','request_id':uuid.uuid4().hex})
    assert r.status_code==200,r.text
    assert r.json()['provider']=='structural_check' and r.json()['result']=='unknown'
    assert r.json()['annotations'][1]['quote']=='because I have a class'


def test_empty_evidence_is_not_zero_mastery():
    assert competency_state([])['state']=='not_started'


def test_four_skill_unit_resume_repair_transfer_and_profile_export(client):
    h=identity(client)
    for skill,answer,transfer in [('reading','9','station'),('listening','five','home'),
                                 ('writing','Could we meet Saturday because I have a class?','We can eat indoors because of rain.'),
                                 ('speaking','I changed my plan because it was raining.','I would choose the train because it is faster.')]:
        url=start(client,h,skill)
        row=client.get(url,headers=h).json()
        r=client.patch(url,headers=h,json={'expected_revision':row['revision'],'step_id':'independent',
            'item_id':'i1','draft':answer,'evidence':'my selected evidence'})
        assert r.status_code==200,r.text
        restored=client.get(url,headers=h).json()
        assert restored['drafts']['independent:i1']==answer
        assert restored['drafts']['independent:evidence']=='my selected evidence'
        submit(client,h,url,'independent','i1',answer)
        submit(client,h,url,'repair','repair1','I checked the reason and corrected my answer.')
        assert submit(client,h,url,'transfer','t1',transfer)['evidence_kind']=='transfer'
    exported=client.get('/api/v1/learning/export',headers=h).json()
    assert len(exported['attempts'])==4 and len(exported['observations'])==12
    assert client.get('/api/v1/learning/export',headers=identity(client)).json()['attempts']==[]
