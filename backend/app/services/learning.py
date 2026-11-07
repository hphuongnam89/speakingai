import hashlib
import json
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.learning import LearningAttemptModel, LearningEventModel, LearningLessonModel, LearningObservationModel, LearningReviewModel
from app.schemas.learning import Lesson
from app.services import learning_progress as progress


def get_lesson(db: Session, lesson_id: str, version: str) -> Lesson:
    row = db.get(LearningLessonModel, (lesson_id, version))
    if not row:
        raise HTTPException(status_code=404, detail="Lesson not found")
    lesson = Lesson.model_validate_json(row.payload_json)
    return lesson.model_copy(update={"status": "retired"}) if row.retired else lesson


def can_preview(preview: bool) -> bool:
    return preview and settings.ENVIRONMENT.lower() in {"development", "testing"}


def visible(lesson: Lesson, preview: bool):
    if lesson.status == "retired":
        raise HTTPException(status_code=404, detail="Lesson retired; only existing attempts can be resumed")
    if lesson.status != "published" and not can_preview(preview):
        raise HTTPException(status_code=404, detail="Lesson not released")


def owned_attempt(db: Session, attempt_id: str, owner: str, profile: str) -> LearningAttemptModel:
    row = db.query(LearningAttemptModel).filter_by(id=attempt_id, owner_user_id=owner, profile_id=profile).first()
    if not row:
        raise HTTPException(status_code=404, detail="Attempt not found")
    return row


def visible_to_learner(db, lesson, preview, owner, profile):
    historical = lesson.status == "retired" and db.query(LearningAttemptModel).filter_by(
        owner_user_id=owner, profile_id=profile, lesson_id=lesson.id, lesson_version=lesson.version).first() is not None
    if not historical:
        visible(lesson, preview)


def get_step(lesson: Lesson, step_id: str):
    step = next((s for s in lesson.steps if s.id == step_id), None)
    if not step:
        raise HTTPException(status_code=422, detail="Unknown lesson step")
    return step


def attempt_payload(db: Session, row: LearningAttemptModel) -> dict:
    return {"id": row.id, "lesson_id": row.lesson_id, "version": row.lesson_version,
            "step_id": row.step_id, "draft": row.draft, "drafts": json.loads(row.drafts_json or "{}"), "revision": row.revision,
            "assistance": json.loads(row.assistance_json),
            "events": [{"action": e.action, "result": json.loads(e.response_json)}
                       for e in db.query(LearningEventModel).filter_by(attempt_id=row.id).order_by(LearningEventModel.created_at, LearningEventModel.id).limit(100)]}


def request_hash(payload) -> str:
    return hashlib.sha256(payload.model_dump_json().encode()).hexdigest()


def cached_event(db, row, action, payload):
    event = db.query(LearningEventModel).filter_by(attempt_id=row.id, action=action, request_id=payload.request_id).first()
    if event:
        if event.request_hash != request_hash(payload):
            raise HTTPException(status_code=409, detail="Request ID was used for different content")
        return json.loads(event.response_json)
    return None


def save_event(db, row, action, payload, result, assistance=None):
    if db.query(LearningEventModel).filter_by(attempt_id=row.id).count() >= 100:
        db.rollback()
        raise HTTPException(status_code=422, detail="Attempt activity limit reached; start a new attempt")
    # Revision compare-and-swap serializes hints, submits and autosaves for one attempt.
    revision = row.revision
    changes = {"revision": revision + 1}
    if assistance is not None:
        changes["assistance_json"] = json.dumps(assistance)
    count = db.query(LearningAttemptModel).filter_by(id=row.id, revision=revision).update(changes, synchronize_session=False)
    if not count:
        db.rollback()
        raise HTTPException(status_code=409, detail="Attempt changed; reload before retrying")
    result["revision"] = revision + 1
    db.add(LearningEventModel(owner_user_id=row.owner_user_id, profile_id=row.profile_id,
                             attempt_id=row.id, request_id=payload.request_id, action=action,
                             request_hash=request_hash(payload), response_json=json.dumps(result, ensure_ascii=False)))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        found = cached_event(db, row, action, payload)
        if found is not None:
            return found
        raise HTTPException(status_code=409, detail="Concurrent request; reload and retry")
    return result


def assistance_for(row, step_id):
    return json.loads(row.assistance_json).get(step_id, {"max_hint_level": 0, "answer_revealed": False, "tutor_used": False})


def _normalise(value: str) -> str:
    return " ".join(value.strip().casefold().split())


def _mark_item(item, text: str):
    if item.answer is None:
        return "unknown"
    answers = [item.answer, *getattr(item, "answer_variants", [])]
    if getattr(item, "max_words", None) and len(text.split()) > item.max_words:
        return "not_yet"
    return "met" if any(_normalise(text) == _normalise(answer) for answer in answers) else "not_yet"


def review_payload(review, now=None):
    now = now or datetime.now(timezone.utc)
    next_review_at = review.next_review_at
    if next_review_at.tzinfo is None:
        next_review_at = next_review_at.replace(tzinfo=timezone.utc)
    due = next_review_at <= now
    return {"id": review.id, "lesson_id": review.lesson_id, "version": review.lesson_version,
            "item_id": review.item_id, "competency_id": review.competency_id,
            "state": review.state, "due": due, "next_review_at": next_review_at.isoformat(),
            "last_result": review.last_result, "last_evidence_kind": review.last_evidence_kind}


def submit(db: Session, row, lesson, payload):
    cached = cached_event(db, row, "submit", payload)
    if cached is not None:
        return cached
    step = get_step(lesson, payload.step_id)
    item = next((i for i in step.items if i.id == payload.item_id), None)
    if not item:
        raise HTTPException(status_code=422, detail="Unknown activity item")
    aid = assistance_for(row, step.id)
    if payload.turn_id:
        import uuid
        from app.models.turn import TurnModel
        session_id = str(uuid.uuid5(uuid.NAMESPACE_URL, "learning:" + row.id))
        turn = db.query(TurnModel).filter_by(id=payload.turn_id, session_id=session_id,
            owner_user_id=row.owner_user_id, role="user").first()
        if lesson.skill != "speaking" or not turn:
            raise HTTPException(status_code=422, detail="Recording does not belong to this lesson")
    prior = db.query(LearningObservationModel).filter_by(owner_user_id=row.owner_user_id, profile_id=row.profile_id,
             lesson_id=row.lesson_id, item_id=item.id).first()
    supported = aid["max_hint_level"] > 0 or aid["tutor_used"] or aid["answer_revealed"] or prior is not None
    kind = "assisted" if supported or step.kind == "guided" else {"independent": "independent", "transfer": "transfer", "self_repair": "correction_uptake"}.get(step.kind, "assisted")
    result = _mark_item(item, payload.text)
    evidence_match = None
    if lesson.skill == "reading" and payload.evidence:
        selected = _normalise(payload.evidence)
        evidence_match = selected in _normalise(step.stimulus) and selected in _normalise(item.evidence) and _normalise(item.answer or "") in selected
        if not evidence_match and result == "met":
            result = "not_yet"
    if step.kind == "review":
        review = db.query(LearningReviewModel).filter_by(owner_user_id=row.owner_user_id,
            profile_id=row.profile_id, lesson_id=lesson.id, lesson_version=lesson.version,
            item_id="__competency__").first()
        if not review or progress.utc(review.next_review_at) > datetime.now(timezone.utc):
            raise HTTPException(status_code=409, detail="Review is not due yet")
        candidate = progress.next_review_item(db, row, lesson)
        if not prior and (not candidate or candidate[1].id != item.id):
            raise HTTPException(status_code=409, detail="Choose the next unseen review item")
        kind = "assisted" if supported else "retention"
    # Prior item submissions prevent counting the same revealed answer as new evidence.
    response = {"result": result, "evidence_kind": kind, "item_id": item.id,
                "learner_text": payload.text,
                "answer": item.answer, "evidence": item.evidence, "evidence_match": evidence_match,
                "assessment_band": None,
                "next_action": "Hãy giải thích hoặc tự sửa, sau đó thử ngữ liệu mới." if item.answer is not None
                               else "Đã lưu bài. Mở Tutor để nhận gợi ý theo mục tiêu rồi tự sửa; chưa có kết luận năng lực."}
    db.add(LearningObservationModel(owner_user_id=row.owner_user_id, profile_id=row.profile_id,
        attempt_id=row.id, lesson_id=row.lesson_id, lesson_version=row.lesson_version, item_id=item.id,
        competency_id=lesson.competency_id, evidence_kind=kind, result=result,
        response_text=payload.text, policy_version=progress.POLICY,
        assistance_json=json.dumps({**aid, "content_seen_before": prior is not None, "selected_evidence": payload.evidence,
            "turn_id": payload.turn_id, "input_modality": "audio_transcript" if payload.turn_id else "text"})))
    progress.schedule(db, row, lesson, kind, result)
    return save_event(db, row, "submit", payload, response)


def delete_learning_data(db, owner, profile=None):
    for model in (LearningReviewModel, LearningObservationModel, LearningEventModel, LearningAttemptModel):
        query = db.query(model).filter_by(owner_user_id=owner)
        if profile is not None:
            query = query.filter_by(profile_id=profile)
        query.delete(synchronize_session=False)
