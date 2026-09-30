from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.schemas.conversation import ConversationRequest, ConversationResponse, Correction
from app.repositories.session_repo import SessionRepository
from app.repositories.turn_repo import TurnRepository
from app.repositories.mistake_repo import MistakeRepository
from app.repositories.settings_repo import SettingsRepository
from app.services.llm.router import get_model_router
from app.prompts.tutor import build_conversation_messages, parse_corrections
from app.core.auth import get_current_user_id

router = APIRouter(prefix="/conversation", tags=["conversation"])

@router.post("/respond", response_model=ConversationResponse)
async def get_response(req: ConversationRequest, request: Request, db: Session = Depends(get_db)):
    session_repo = SessionRepository(db)
    turn_repo = TurnRepository(db)
    mistake_repo = MistakeRepository(db)
    settings_repo = SettingsRepository(db)
    
    session = session_repo.get(req.session_id, get_current_user_id(request))
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Audio transcription stores the candidate turn before calling this route.
    # Reuse that last turn when the transcript matches to avoid duplicating it
    # in session history (Android and web voice flows both use this sequence).
    turns = turn_repo.get_by_session(req.session_id)
    if (
        turns
        and turns[-1].role == "user"
        and turns[-1].transcript.strip() == req.user_text.strip()
    ):
        user_turn = turns[-1]
    else:
        user_turn = turn_repo.create(
            session_id=req.session_id,
            role="user",
            transcript=req.user_text
        )
        turns = turn_repo.get_by_session(req.session_id)

    # Load all turns and convert to message dicts
    turn_dicts = [{"role": t.role, "content": t.transcript} for t in turns]
    
    # Load user settings for model routing even when the request overrides the
    # correction level. The settings are also the fallback for that level.
    user_settings = settings_repo.get_or_create(session.user_id)
    correction_level = req.correction_level or user_settings.correction_level or "important"

    messages = build_conversation_messages(
        mode=session.mode,
        turns=turn_dicts,
        topic=session.topic,
        correction_level=correction_level
    )
    
    model_router = get_model_router()
    options = {
        "preference": getattr(user_settings, "provider_preference", "auto"),
        "local_only": getattr(user_settings, "local_only", False),
        "cloud_fallback": getattr(user_settings, "cloud_fallback", False),
        # Local model replies can take longer than the provider's short default
        # timeout, especially on the first turn after loading a model.
        "timeout": settings.LLM_TIMEOUT,
    }
    response_text, meta = await model_router.chat_with_metadata(messages, options)
    
    clean_reply, corrections, repeat_prompt = parse_corrections(response_text)
    
    if correction_level == "none":
        corrections = []
        repeat_prompt = None
    
    # Save assistant turn
    assistant_turn = turn_repo.create(
        session_id=req.session_id,
        role="assistant",
        transcript=clean_reply
    )

    # Persist mistakes and count recurring occurrences
    if correction_level != "none":
        for c in corrections:
            mistake_repo.record_mistake(
                user_id=session.user_id,
                session_id=session.id,
                turn_id=str(user_turn.id) if user_turn else None,
                original=c["original"],
                corrected=c["corrected"],
                explanation=c.get("explanation"),
                category=c.get("category", "grammar")
            )

    # Record daily speaking progress
    from app.repositories.progress_repo import ProgressRepository
    words_count = len(req.user_text.split())
    ProgressRepository(db).record_activity(
        user_id=session.user_id,
        speaking_minutes=round(max(words_count / 110.0, 0.25), 2),
        words=words_count,
        mistakes=len(corrections) if correction_level != "none" else 0
    )
    
    return ConversationResponse(
        message=clean_reply,
        corrections=[Correction(**c) for c in corrections],
        repeat_prompt=repeat_prompt,
        tts_text=clean_reply,
        turn_id=str(assistant_turn.id) if assistant_turn else None,
        pronunciation=None,
        provider_used=meta.get("provider_used"),
        fallback_triggered=meta.get("fallback_triggered", False),
        latency_ms=meta.get("latency_ms")
    )

