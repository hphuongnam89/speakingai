import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories.progress_repo import ProgressRepository
from app.repositories.mistake_repo import MistakeRepository
from app.repositories.session_repo import SessionRepository
from app.services.llm.router import get_model_router
from app.prompts.adaptive import build_adaptive_plan_messages, parse_adaptive_plan
from app.schemas.progress import (
    ProgressSummaryResponse,
    DailyStatItem,
    AdaptivePlanResponse
)
from app.core.auth import get_current_user_id, get_current_principal_id

router = APIRouter(prefix="/progress", tags=["progress"])

@router.get("/summary", response_model=ProgressSummaryResponse)
def get_progress_summary(request: Request, db: Session = Depends(get_db)):
    user_id = get_current_user_id(request)
    repo = ProgressRepository(db)
    data = repo.get_summary(user_id, get_current_principal_id(request))
    return ProgressSummaryResponse(**data)

@router.get("/weekly", response_model=list[DailyStatItem])
def get_weekly_progress(request: Request, db: Session = Depends(get_db)):
    user_id = get_current_user_id(request)
    repo = ProgressRepository(db)
    items = repo.get_weekly_stats(user_id, get_current_principal_id(request))
    return [DailyStatItem(**item) for item in items]

@router.get("/adaptive-plan", response_model=AdaptivePlanResponse)
async def get_adaptive_daily_plan(request: Request, db: Session = Depends(get_db)):
    user_id = get_current_user_id(request)
    mistake_repo = MistakeRepository(db)
    session_repo = SessionRepository(db)

    # 1. Fetch recurring mistakes
    owner_user_id = get_current_principal_id(request)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    from app.models.adaptive_plan import AdaptivePlanModel
    cached = db.query(AdaptivePlanModel).filter(
        AdaptivePlanModel.owner_user_id == owner_user_id,
        AdaptivePlanModel.plan_date == today,
    ).first()
    if cached:
        return AdaptivePlanResponse(**json.loads(cached.payload_json))
    frequent_mistakes = mistake_repo.get_frequent_mistakes(user_id, limit=6, owner_user_id=owner_user_id)
    mistake_dicts = [
        {
            "original_text": m.original_text,
            "corrected_text": m.corrected_text,
            "occurrence_count": m.occurrence_count,
            "explanation": m.explanation
        }
        for m in frequent_mistakes
    ]

    # 2. Fetch recent topics
    recent_sessions = session_repo.list_recent(limit=5, user_id=user_id, owner_user_id=owner_user_id)
    recent_topics = [s.topic for s in recent_sessions if s.topic]

    # 3. Generate adaptive plan with Ollama
    messages = build_adaptive_plan_messages(
        mistakes=mistake_dicts,
        recent_topics=recent_topics
    )

    model_router = get_model_router()
    response_text = await model_router.chat(messages)
    plan_data = parse_adaptive_plan(response_text)
    evidence_count = len(frequent_mistakes)
    plan_data["plan_date"] = today
    plan_data["evidence_count"] = evidence_count
    plan_data["next_best_action"] = f"Complete a focused speaking session using one of today's challenge phrases; evidence items: {evidence_count}."
    db.add(AdaptivePlanModel(
        owner_user_id=owner_user_id,
        plan_date=today,
        payload_json=json.dumps(plan_data, ensure_ascii=False),
        evidence_count=str(evidence_count),
    ))
    db.commit()

    return AdaptivePlanResponse(**plan_data)
