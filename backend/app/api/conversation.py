from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.schemas.conversation import ConversationRequest, ConversationResponse, Correction, RepeatCheckRequest, RepeatCheckResponse
from app.repositories.session_repo import SessionRepository
from app.repositories.turn_repo import TurnRepository
from app.repositories.mistake_repo import MistakeRepository
from app.repositories.settings_repo import SettingsRepository
from app.services.llm.router import get_model_router
from app.prompts.tutor import build_conversation_messages, parse_corrections
from app.core.auth import get_current_user_id, get_current_principal_id

router = APIRouter(prefix="/conversation", tags=["conversation"])

@router.post("/repeat-check", response_model=RepeatCheckResponse)
def repeat_check(req: RepeatCheckRequest):
    expected = {word for word in req.expected_text.lower().split() if word.isalnum()}
    actual = {word for word in req.actual_text.lower().split() if word.isalnum()}
    similarity = len(expected & actual) / max(len(expected), 1)
    passed = similarity >= 0.8 and len(req.actual_text.strip()) >= 3
    return RepeatCheckResponse(
        passed=passed,
        similarity=round(similarity, 2),
        feedback="Good reuse—now try it in a new personal example." if passed else "Please say the corrected pattern again, then add your own example.",
    )

@router.post("/respond", response_model=ConversationResponse)
async def get_response(req: ConversationRequest, request: Request, db: Session = Depends(get_db)):
    session_repo = SessionRepository(db)
    turn_repo = TurnRepository(db)
    mistake_repo = MistakeRepository(db)
    settings_repo = SettingsRepository(db)
    
    owner_user_id = get_current_principal_id(request)
    profile_id = get_current_user_id(request)
    session = session_repo.get(req.session_id, profile_id, owner_user_id)
    if not session:
        raise HTTPException(
            status_code=404,
            detail={"error_code": "SESSION_NOT_FOUND", "message": "Session not found", "retryable": False}
        )

    # Prevent calling LLM or adding turns if session has already ended
    if session.ended_at is not None:
        raise HTTPException(
            status_code=400,
            detail={"error_code": "SESSION_ALREADY_FINISHED", "message": "Cannot send answers to an ended session", "retryable": False}
        )

    # Idempotency check: if client retries with the same request_id, return cached response
    existing_user_turn = None
    if req.request_id:
        existing_user_turn = turn_repo.get_by_client_turn_id(req.session_id, req.request_id, owner_user_id)
        if existing_user_turn:
            all_turns = turn_repo.get_by_session(req.session_id, owner_user_id)
            for i, t in enumerate(all_turns):
                if t.id == existing_user_turn.id and i + 1 < len(all_turns) and all_turns[i + 1].role == "assistant":
                    assistant_turn = all_turns[i + 1]
                    clean_reply, corrections, repeat_prompt, upgraded_sentence = parse_corrections(assistant_turn.transcript)
                    return ConversationResponse(
                        message=clean_reply,
                        corrections=[Correction(**c) for c in corrections],
                        upgraded_sentence=upgraded_sentence,
                        repeat_prompt=repeat_prompt,
                        tts_text=clean_reply,
                        turn_id=str(assistant_turn.id),
                        pronunciation=None,
                        provider_used="cached_idempotent",
                        fallback_triggered=False,
                        latency_ms=0.0
                    )

    # Audio transcription stores the candidate turn before calling this route.
    # Reuse that last turn when the transcript matches to avoid duplicating it
    # in session history (Android and web voice flows both use this sequence).
    turns = turn_repo.get_by_session(req.session_id, owner_user_id)
    if existing_user_turn:
        user_turn = existing_user_turn
    elif (
        turns
        and turns[-1].role == "user"
        and turns[-1].transcript.strip() == req.user_text.strip()
    ):
        user_turn = turns[-1]
        if req.request_id and not user_turn.client_turn_id:
            user_turn.client_turn_id = req.request_id
            db.commit()
    else:
        user_turn = turn_repo.create(
            session_id=req.session_id,
            role="user",
            transcript=req.user_text,
            owner_user_id=owner_user_id,
            client_turn_id=req.request_id
        )
        turns = turn_repo.get_by_session(req.session_id, owner_user_id)

    # Load all turns and convert to message dicts
    turn_dicts = [{"role": t.role, "content": t.transcript} for t in turns]
    
    # Load user settings for model routing even when the request overrides the
    # correction level. The settings are also the fallback for that level.
    user_settings = settings_repo.get_or_create(session.user_id)
    correction_level = req.correction_level or user_settings.correction_level or "important"

    # Load Student Profile & Mistake Memory
    from app.repositories.profile_repo import ProfileRepository
    from app.models.mistake import MistakeModel
    profile_repo = ProfileRepository(db)
    profile = profile_repo.get(session.user_id) or profile_repo.get_active()

    unresolved_db_mistakes = (
        db.query(MistakeModel)
        .filter(MistakeModel.user_id == session.user_id, MistakeModel.owner_user_id == owner_user_id, MistakeModel.resolved == False)
        .order_by(MistakeModel.occurrence_count.desc(), MistakeModel.last_seen_at.desc())
        .limit(4)
        .all()
    )
    unresolved_list = [
        {"original": m.original_text, "corrected": m.corrected_text, "explanation": m.explanation}
        for m in unresolved_db_mistakes
    ]

    messages = build_conversation_messages(
        mode=session.mode,
        turns=turn_dicts,
        topic=session.topic,
        correction_level=correction_level,
        student_name=profile.name if profile else None,
        current_band=profile.current_band if profile else None,
        target_band=profile.target_band if profile else None,
        unresolved_mistakes=unresolved_list
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
    
    clean_reply, corrections, repeat_prompt, upgraded_sentence = parse_corrections(response_text)
    
    if correction_level == "none":
        corrections = []
        repeat_prompt = None
        upgraded_sentence = None
    
    # Save assistant turn
    assistant_turn = turn_repo.create(
        session_id=req.session_id,
        role="assistant",
        transcript=clean_reply,
        owner_user_id=owner_user_id
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
                category=c.get("category", "grammar"),
                owner_user_id=owner_user_id,
                error_type=c.get("error_type", c.get("category", "grammar")),
                subtype=c.get("subtype", "general"),
                example_sentence=c.get("corrected")
            )

    # Record daily speaking progress
    from app.repositories.progress_repo import ProgressRepository
    words_count = len(req.user_text.split())
    ProgressRepository(db).record_activity(
        user_id=session.user_id,
        speaking_minutes=round(max(words_count / 110.0, 0.25), 2),
        words=words_count,
        mistakes=len(corrections) if correction_level != "none" else 0,
        owner_user_id=owner_user_id
    )
    
    session_focus = None
    if corrections:
        focus = corrections[0]
        session_focus = f"{focus.get('error_type', focus.get('category', 'language')).title()}: {focus.get('subtype', 'general').replace('_', ' ')}"

    return ConversationResponse(
        message=clean_reply,
        corrections=[Correction(**c) for c in corrections],
        repeat_prompt=repeat_prompt,
        upgraded_sentence=upgraded_sentence,
        session_focus=session_focus,
        tts_text=clean_reply,
        turn_id=str(assistant_turn.id) if assistant_turn else None,
        pronunciation=None,
        provider_used=meta.get("provider_used"),
        fallback_triggered=meta.get("fallback_triggered", False),
        latency_ms=meta.get("latency_ms")
    )
