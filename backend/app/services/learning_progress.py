"""Replayable pilot policy: content exposure and unknown results never imply mastery."""
from datetime import datetime, timedelta, timezone

from app.models.learning import LearningObservationModel, LearningReviewModel

POLICY = "learning-pilot-0.2"


def utc(value):
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value


def competency_state(observations):
    fresh = [o for o in observations if o.evidence_kind in {"independent", "transfer"}]
    known = [o for o in fresh if o.result != "unknown"]
    # The v0.2 pack retains v0.1 item IDs/text: a version bump is not fresh evidence.
    unique = {(o.lesson_id, o.item_id): o for o in known}
    met = sum(o.result == "met" for o in unique.values())
    retention = [o for o in observations if o.evidence_kind == "retention"]
    state = "not_started" if not observations else "learning"
    if fresh:
        state = "practicing"
    if len(unique) >= 4 and met >= 3:
        state = "provisionally_mastered"
    if retention and retention[-1].result == "not_yet":
        state = "needs_review"
    return {"state": state, "independent_items": len({(o.lesson_id, o.item_id) for o in fresh}),
            "assessed_items": len(unique), "unknown_items": sum(o.result == "unknown" for o in fresh), "met_items": met,
            "transfer_items": sum(o.evidence_kind == "transfer" for o in fresh),
            "retention_items": sum(o.result == "met" for o in retention),
            "evidence_ids": [o.id for o in observations], "policy_version": POLICY}


def observations_for(db, owner, profile, competency):
    return db.query(LearningObservationModel).filter_by(owner_user_id=owner, profile_id=profile,
        competency_id=competency).order_by(LearningObservationModel.created_at, LearningObservationModel.id).all()


def schedule(db, row, lesson, kind, result, now=None):
    now = now or datetime.now(timezone.utc)
    db.flush()
    observations = observations_for(db, row.owner_user_id, row.profile_id, lesson.competency_id)
    state = competency_state(observations)
    review = db.query(LearningReviewModel).filter_by(owner_user_id=row.owner_user_id,
        profile_id=row.profile_id, lesson_id=lesson.id, lesson_version=lesson.version, item_id="__competency__").first()
    if review is None and state["state"] == "provisionally_mastered":
        review = LearningReviewModel(owner_user_id=row.owner_user_id, profile_id=row.profile_id,
            lesson_id=lesson.id, lesson_version=lesson.version, item_id="__competency__",
            competency_id=lesson.competency_id, state="provisionally_mastered", interval_days=2,
            next_review_at=now + timedelta(days=2), last_result=result, last_evidence_kind=kind)
        db.add(review)
    elif review and kind == "retention":
        review.state = "provisionally_mastered" if result == "met" else "needs_review"
        review.interval_days = 7 if result == "met" else 2
        review.next_review_at = now + timedelta(days=review.interval_days)
        review.last_result, review.last_evidence_kind = result, kind
        review.updated_at = now
    return state


def next_review_item(db, row, lesson):
    seen = {o.item_id for o in observations_for(db, row.owner_user_id, row.profile_id, lesson.competency_id)
            if o.lesson_id == lesson.id and o.lesson_version == lesson.version}
    for step in lesson.steps:
        if step.kind == "review":
            for item in step.items:
                if item.id not in seen:
                    return step, item
    return None
