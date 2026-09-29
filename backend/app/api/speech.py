import os
import shutil
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.repositories.turn_repo import TurnRepository
from app.services.stt.whisper_service import get_whisper_service
from app.schemas.speech import TranscribeResponse, AudioMetrics

router = APIRouter(prefix="/speech", tags=["speech"])

@router.post("/transcribe", response_model=TranscribeResponse)
def transcribe_audio(
    audio: UploadFile = File(...),
    session_id: str = Form(...),
    turn_id: str | None = Form(None),
    db: Session = Depends(get_db)
):
    session_audio_dir = os.path.join(settings.AUDIO_DIR, session_id)
    os.makedirs(session_audio_dir, exist_ok=True)
    
    file_path = os.path.join(session_audio_dir, audio.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)
        
    whisper_service = get_whisper_service()
    result = whisper_service.transcribe(file_path)
    
    metrics = whisper_service.calculate_metrics(
        result["segments"], result["text"], result["duration_ms"]
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
        turn_id=str(turn.id) if turn else None
    )
