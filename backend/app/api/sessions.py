import os
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.schemas.session import SessionCreate, SessionResponse
from app.repositories.session_repo import SessionRepository
from app.repositories.turn_repo import TurnRepository
from app.models.turn import TurnModel
from app.models.mistake import MistakeModel
from app.core.auth import get_current_user_id, get_current_principal_id

router = APIRouter(prefix="/sessions", tags=["sessions"])

@router.post("/", response_model=SessionResponse)
def create_session(session_data: SessionCreate, request: Request, db: Session = Depends(get_db)):
    repo = SessionRepository(db)
    session = repo.create(session_data, user_id=get_current_user_id(request), owner_user_id=get_current_principal_id(request))
    return session

@router.get("/")
def list_sessions(
    request: Request,
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    user_id = get_current_user_id(request)
    sessions = SessionRepository(db).list_recent(limit=limit, user_id=user_id, owner_user_id=get_current_principal_id(request))
    session_ids = [s.id for s in sessions]
    turn_counts = {}
    if session_ids:
        counts = db.query(TurnModel.session_id, func.count(TurnModel.id)).filter(TurnModel.session_id.in_(session_ids)).group_by(TurnModel.session_id).all()
        turn_counts = dict(counts)
        
    res = []
    for s in sessions:
        res.append({
            "id": s.id,
            "mode": s.mode,
            "topic": s.topic or "Luyện nói tự do",
            "started_at": s.started_at.isoformat() if s.started_at else None,
            "ended_at": s.ended_at.isoformat() if s.ended_at else None,
            "total_speaking_ms": s.total_speaking_ms or 0,
            "turns_count": turn_counts.get(s.id, 0),
            "estimated_band": s.estimated_band
        })
    return res

@router.get("/{session_id}")
def get_session(session_id: str, request: Request, db: Session = Depends(get_db)):
    repo = SessionRepository(db)
    turn_repo = TurnRepository(db)
    session = repo.get(session_id, get_current_user_id(request), get_current_principal_id(request))
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    turns = turn_repo.get_by_session(session_id, get_current_principal_id(request))
    mistakes = db.query(MistakeModel).filter(MistakeModel.session_id == session_id).all()
    
    turns_data = []
    for t in turns:
        has_audio = bool(t.audio_path and os.path.exists(t.audio_path))
        turns_data.append({
            "id": str(t.id),
            "role": t.role,
            "transcript": t.transcript,
            "has_audio": has_audio,
            "audio_url": f"/api/v1/speech/audio/{t.id}" if has_audio else None,
            "duration_ms": t.duration_ms,
            "created_at": t.created_at.isoformat() if t.created_at else None
        })
        
    return {
        "session": {
            "id": session.id,
            "mode": session.mode,
            "topic": session.topic,
            "started_at": session.started_at.isoformat() if session.started_at else None,
            "ended_at": session.ended_at.isoformat() if session.ended_at else None,
            "total_speaking_ms": session.total_speaking_ms,
            "estimated_band": session.estimated_band
        },
        "turns": turns_data,
        "mistakes": [
            {
                "id": str(m.id),
                "original": m.original_text,
                "corrected": m.corrected_text,
                "explanation": m.explanation,
                "category": m.category
            }
            for m in mistakes
        ]
    }

@router.post("/{session_id}/finish", response_model=SessionResponse)
def finish_session(session_id: str, request: Request, db: Session = Depends(get_db)):
    repo = SessionRepository(db)
    session = repo.finish(session_id, get_current_user_id(request), get_current_principal_id(request))
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session
