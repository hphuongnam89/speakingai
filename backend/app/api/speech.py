import os
import shutil
import uuid
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.repositories.turn_repo import TurnRepository
from app.repositories.session_repo import SessionRepository
from app.services.stt.whisper_service import get_whisper_service, get_whisper_status
from app.schemas.speech import TranscribeResponse, AudioMetrics
from app.core.auth import get_current_user_id

router = APIRouter(prefix="/speech", tags=["speech"])


@router.get("/status")
def speech_status():
    """Report local speech recognition capability without loading/downloading a model."""
    return get_whisper_status()

@router.post("/transcribe", response_model=TranscribeResponse)
def transcribe_audio(
    request: Request,
    audio: UploadFile = File(...),
    session_id: str = Form(...),
    turn_id: str | None = Form(None),
    db: Session = Depends(get_db)
):
    if not session_id or len(session_id) > 128 or not all(char.isalnum() or char in "-_" for char in session_id):
        raise HTTPException(status_code=400, detail="Invalid session_id")

    owned_session = SessionRepository(db).get(session_id, get_current_user_id(request))
    if not owned_session:
        raise HTTPException(status_code=404, detail="Session not found")

    session_audio_dir = os.path.join(settings.AUDIO_DIR, session_id)
    os.makedirs(session_audio_dir, exist_ok=True)

    suffix = Path(audio.filename or "recording.m4a").suffix.lower()
    if suffix not in {".wav", ".mp3", ".m4a", ".mp4", ".webm", ".ogg", ".flac"}:
        suffix = ".audio"
    file_path = os.path.join(session_audio_dir, f"{uuid.uuid4().hex}{suffix}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)
        
    whisper_service = get_whisper_service()
    result = whisper_service.transcribe(file_path)
    if result.get("error"):
        try:
            os.remove(file_path)
        except OSError:
            pass
        raise HTTPException(status_code=503, detail=result["error"])
    
    metrics = whisper_service.calculate_metrics(
        result["segments"], result["text"], result["duration_ms"]
    )

    from app.services.pronunciation.pronunciation_service import get_pronunciation_service
    word_data = [word for segment in result["segments"] for word in segment["words"]]
    pronunciation = get_pronunciation_service().analyze_speech(
        text=result["text"],
        segments=result["segments"],
        words_data=word_data,
        duration_ms=result["duration_ms"],
        audio_path=file_path,
    )
    
    turn_repo = TurnRepository(db)
    turn = turn_repo.create(
        session_id=session_id,
        role="user",
        transcript=result["text"],
        audio_path=file_path,
        duration_ms=result["duration_ms"]
    )
    
    return TranscribeResponse(
        text=result["text"],
        duration_ms=result["duration_ms"],
        language=result["language"],
        metrics=metrics,
        turn_id=str(turn.id) if turn else None,
        pronunciation=pronunciation,
    )
