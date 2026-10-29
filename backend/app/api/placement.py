from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.core.auth import get_current_principal_id
from app.repositories.profile_repo import ProfileRepository
from app.services.llm.router import get_model_router
from app.prompts.placement import (
    PLACEMENT_QUESTIONS,
    build_placement_eval_messages,
    parse_placement_result,
)

router = APIRouter(prefix="/placement", tags=["placement"])


class AnswerItem(BaseModel):
    question_id: int
    question: str
    answer: str = Field(..., min_length=2)


class PlacementEvaluateRequest(BaseModel):
    profile_id: str
    answers: List[AnswerItem]


class PlacementEvaluateResponse(BaseModel):
    profile_id: str
    estimated_band: float
    fluency_score: float
    lexical_score: float
    grammar_score: float
    pronunciation_score: float
    pronunciation_feedback: Optional[str] = None
    key_weaknesses: List[str]
    strengths: List[str]
    examiner_verdict: str
    roadmap: Dict[str, Any]


@router.get("/questions")
def get_placement_questions():
    """
    Returns the standard 3 diagnostic questions for level placement.
    """
    return {"questions": PLACEMENT_QUESTIONS}


@router.post("/evaluate", response_model=PlacementEvaluateResponse)
async def evaluate_placement(data: PlacementEvaluateRequest, request: Request, db: Session = Depends(get_db)):
    repo = ProfileRepository(db)
    profile = repo.get(data.profile_id, get_current_principal_id(request))
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    if len(data.answers) < 3:
        raise HTTPException(status_code=400, detail="Vui lòng hoàn thành cả 3 câu hỏi kiểm tra đầu vào.")

    # Convert answers to prompt format
    formatted_answers = [
        {"question": a.question, "answer": a.answer}
        for a in data.answers
    ]

    messages = build_placement_eval_messages(
        answers=formatted_answers,
        target_band=profile.target_band,
        daily_minutes=profile.daily_target_minutes,
        duration_months=profile.target_duration_months
    )

    model_router = get_model_router()
    options = {
        "preference": "local_only",
        "local_only": True,
        "cloud_fallback": False,
        "timeout": settings.LLM_TIMEOUT,
        "num_ctx": 4096,
        "max_tokens": 1536,
    }

    try:
        response_text, meta = await model_router.chat_with_metadata(messages, options)
    except Exception:
        raise HTTPException(status_code=503, detail="Placement evaluation is temporarily unavailable")

    eval_result = parse_placement_result(response_text)
    estimated_band = float(eval_result.get("estimated_band", 5.0))

    # Save to profile in SQLite
    repo.update_placement_result(
        profile_id=profile.id,
        current_band=estimated_band,
        roadmap_data=eval_result,
        owner_user_id=get_current_principal_id(request)
    )

    return PlacementEvaluateResponse(
        profile_id=profile.id,
        estimated_band=estimated_band,
        fluency_score=float(eval_result.get("fluency_score", estimated_band)),
        lexical_score=float(eval_result.get("lexical_score", estimated_band)),
        grammar_score=float(eval_result.get("grammar_score", estimated_band)),
        pronunciation_score=float(eval_result.get("pronunciation_score", estimated_band)),
        pronunciation_feedback=eval_result.get("pronunciation_feedback"),
        key_weaknesses=eval_result.get("key_weaknesses", []),
        strengths=eval_result.get("strengths", []),
        examiner_verdict=eval_result.get("examiner_verdict", "Đã hoàn thành kiểm tra đầu vào."),
        roadmap=eval_result.get("roadmap", {})
    )

