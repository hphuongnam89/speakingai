from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.session import SessionCreate, SessionResponse
from app.repositories.session_repo import SessionRepository
from app.repositories.turn_repo import TurnRepository

router = APIRouter(prefix="/sessions", tags=["sessions"])

@router.post("/", response_model=SessionResponse)
def create_session(session_data: SessionCreate, db: Session = Depends(get_db)):
    repo = SessionRepository(db)
    session = repo.create(session_data)
    return session

@router.get("/{session_id}")
def get_session(session_id: str, db: Session = Depends(get_db)):
    repo = SessionRepository(db)
    turn_repo = TurnRepository(db)
    session = repo.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    turns = turn_repo.get_by_session(session_id)
    return {"session": session, "turns": turns}

@router.post("/{session_id}/finish", response_model=SessionResponse)
def finish_session(session_id: str, db: Session = Depends(get_db)):
    repo = SessionRepository(db)
    session = repo.finish(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session
