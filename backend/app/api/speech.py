import os
import shutil
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.repositories.turn_repo import TurnRepository
from app.repositories.session_repo import SessionRepository
from app.services.stt.whisper_service import get_whisper_service, get_whisper_status
from app.schemas.speech import TranscribeResponse, AudioMetrics
from app.core.auth import get_current_user_id, get_current_principal_id
from app.models.audio import AudioRecordingModel

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

    # Normalize and validate content type (strip MIME parameters like codecs=opus)
    raw_content_type = (audio.content_type or "").split(";")[0].strip().lower()
    allowed_types = {
        "audio/webm", "video/webm",
        "audio/ogg", "application/ogg", "audio/opus",
        "audio/wav", "audio/x-wav", "audio/wave",
        "audio/mpeg", "audio/mp3",
        "audio/mp4", "video/mp4", "audio/m4a", "audio/x-m4a", "audio/aac",
        "audio/flac", "audio/x-flac",
        "application/octet-stream", ""
    }
    if raw_content_type and raw_content_type not in allowed_types:
        raise HTTPException(status_code=415, detail=f"Unsupported audio content type: {audio.content_type}")

    is_placement = session_id.startswith("placement") or session_id in {"standalone", "quick-check"}
    if not is_placement:
        owned_session = SessionRepository(db).get(session_id, get_current_user_id(request), get_current_principal_id(request))
        if not owned_session:
            raise HTTPException(status_code=404, detail="Session not found")

    session_audio_dir = os.path.join(settings.AUDIO_DIR, session_id)
    os.makedirs(session_audio_dir, exist_ok=True)

    suffix = Path(audio.filename or "recording.webm").suffix.lower()
    if suffix not in {".wav", ".mp3", ".m4a", ".mp4", ".webm", ".ogg", ".flac", ".opus", ".aac"}:
        if "webm" in raw_content_type:
            suffix = ".webm"
        elif "ogg" in raw_content_type or "opus" in raw_content_type:
            suffix = ".ogg"
        elif "wav" in raw_content_type:
            suffix = ".wav"
        elif "mp4" in raw_content_type or "m4a" in raw_content_type:
            suffix = ".m4a"
        elif "mp3" in raw_content_type or "mpeg" in raw_content_type:
            suffix = ".mp3"
        else:
            suffix = ".webm"
    file_path = os.path.join(session_audio_dir, f"{uuid.uuid4().hex}{suffix}")
    total_bytes = 0
    with open(file_path, "wb") as buffer:
        while chunk := audio.file.read(1024 * 1024):
            total_bytes += len(chunk)
            if total_bytes > settings.MAX_AUDIO_BYTES:
                buffer.close()
                os.remove(file_path)
                raise HTTPException(status_code=413, detail="Audio file exceeds configured size limit")
            buffer.write(chunk)
        
    whisper_service = get_whisper_service()
    result = whisper_service.transcribe(file_path)
    if result.get("error"):
        try:
            os.remove(file_path)
        except OSError:
            pass
        raise HTTPException(status_code=503, detail="Speech transcription is temporarily unavailable")
    
    if result.get("duration_ms", 0) > settings.MAX_AUDIO_DURATION_MS:
        try: os.remove(file_path)
        except OSError: pass
        raise HTTPException(status_code=413, detail="Audio duration exceeds configured limit")

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
    
    turn_id_str = None
    if not is_placement:
        turn_repo = TurnRepository(db)
        owned_session.audio_duration_ms = (owned_session.audio_duration_ms or 0) + int(result["duration_ms"])
        owned_session.actual_speaking_ms = (owned_session.actual_speaking_ms or 0) + int(result["duration_ms"])
        owned_session.total_speaking_ms = (owned_session.total_speaking_ms or 0) + int(result["duration_ms"])
        turn = turn_repo.create(
            session_id=session_id,
            role="user",
            transcript=result["text"],
            audio_path=file_path,
            duration_ms=result["duration_ms"],
            owner_user_id=get_current_principal_id(request)
        )
        turn_id_str = str(turn.id) if turn else None
        db.add(AudioRecordingModel(
            owner_user_id=get_current_principal_id(request),
            session_id=session_id,
            turn_id=turn_id_str,
            file_path=file_path,
            content_type=audio.content_type or "application/octet-stream",
            size_bytes=total_bytes,
            duration_ms=result.get("duration_ms"),
            retention_at=datetime.now(timezone.utc) + timedelta(hours=settings.AUDIO_RETENTION_HOURS),
        ))
        db.commit()
    elif settings.DELETE_AUDIO_AFTER_TRANSCRIPTION:
        try:
            os.remove(file_path)
        except OSError:
            pass

    audio_url = f"/api/v1/speech/audio/{turn_id_str}" if turn_id_str else None

    return TranscribeResponse(
        text=result["text"],
        duration_ms=result["duration_ms"],
        language=result["language"],
        metrics=metrics,
        turn_id=turn_id_str,
        audio_url=audio_url,
        pronunciation=pronunciation,
    )


@router.get("/audio/{turn_id}")
def get_turn_audio(turn_id: str, db: Session = Depends(get_db)):
    rec = db.query(AudioRecordingModel).filter(AudioRecordingModel.turn_id == turn_id).first()
    if rec and rec.file_path and os.path.exists(rec.file_path):
        media_type = rec.content_type or "audio/webm"
        return FileResponse(rec.file_path, media_type=media_type)
    
    # Fallback to TurnModel.audio_path
    from app.models.turn import TurnModel
    turn = db.query(TurnModel).filter(TurnModel.id == turn_id).first()
    if turn and turn.audio_path and os.path.exists(turn.audio_path):
        return FileResponse(turn.audio_path, media_type="audio/webm")
        
    raise HTTPException(status_code=404, detail="Audio recording not found")
