from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.core.auth import get_current_principal_id
from app.repositories.profile_repo import ProfileRepository
from app.services.llm.router import get_model_router
from app.services.assessment import VERSION, MIN_WORDS, parse_payload
from app.prompts.placement import (
    PLACEMENT_QUESTIONS,
    build_placement_eval_messages,
    parse_placement_result,
)

router = APIRouter(prefix="/placement", tags=["placement"])


class AnswerItem(BaseModel):
    question_id: int
    question: str = Field(max_length=2000)
    answer: str = Field(min_length=2, max_length=4000)


class PlacementEvaluateRequest(BaseModel):
    profile_id: str = Field(min_length=1, max_length=128)
    answers: List[AnswerItem] = Field(min_length=3, max_length=3)


class PlacementPhase(BaseModel):
    phase_name: str = Field(min_length=1, max_length=200)
    focus_areas: list[str] = Field(max_length=6)


class PlacementRoadmap(BaseModel):
    phases: list[PlacementPhase] = Field(default_factory=list, max_length=3)


class PlacementEvaluateResponse(BaseModel):
    profile_id: str
    estimated_band: Optional[float] = None
    fluency_score: Optional[float] = None
    lexical_score: float
    grammar_score: float
    pronunciation_score: Optional[float] = None
    pronunciation_feedback: Optional[str] = None
    key_weaknesses: List[str]
    strengths: List[str]
    examiner_verdict: str
    roadmap: Dict[str, Any]
    score_status: str = "provisional"
    calibration_status: str = "unverified"
    scoring_version: str = VERSION
    prompt_version: str = "placement-transcript-0.4"
    provider: Optional[str] = None
    model_id: Optional[str] = None


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

    questions = {q["id"]: q["question"] for q in PLACEMENT_QUESTIONS}
    if {a.question_id for a in data.answers} != questions.keys() or any(not a.answer.strip() for a in data.answers):
        raise HTTPException(status_code=422, detail="Vui lòng hoàn thành đúng 3 câu hỏi kiểm tra đầu vào.")
    if sum(len(a.answer.split()) for a in data.answers) < MIN_WORDS:
        raise HTTPException(status_code=422, detail=f"Chưa đủ ngữ liệu để đánh giá. Hãy mở rộng ba câu trả lời (ít nhất {MIN_WORDS} từ tổng cộng).")

    # Convert answers to prompt format
    formatted_answers = [
        {"question": questions[a.question_id], "answer": a.answer}
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
    validated = parse_payload({**eval_result, "areas_for_improvement": eval_result.get("key_weaknesses", []),
                               "examiner_summary": eval_result.get("examiner_verdict", "")})
    if validated["score_status"] != "provisional" or not meta.get("model_used") or not meta.get("provider_used"):
        raise HTTPException(status_code=502, detail="Không xác minh được góp ý đầu vào. Câu trả lời vẫn giữ nguyên để thử lại.")
    try:
        roadmap = PlacementRoadmap.model_validate(eval_result.get("roadmap", {})).model_dump()
    except ValidationError:
        raise HTTPException(status_code=502, detail="Không xác minh được lộ trình đầu vào. Hãy thử lại.")
    result = PlacementEvaluateResponse(profile_id=profile.id, lexical_score=validated["lexical_score"],
        grammar_score=validated["grammar_score"], pronunciation_feedback="Chưa đánh giá từ transcript.",
        key_weaknesses=validated["areas_for_improvement"], strengths=validated["strengths"],
        examiner_verdict=validated["examiner_summary"], roadmap=roadmap,
        provider=meta["provider_used"], model_id=meta["model_used"])

    # Save to profile in SQLite
    repo.update_placement_result(
        profile_id=profile.id,
        current_band=None,
        roadmap_data=result.model_dump(exclude={"profile_id"}),
        owner_user_id=get_current_principal_id(request)
    )

    return result

