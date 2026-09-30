from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.session import SessionCreate, SessionResponse
from app.repositories.session_repo import SessionRepository
from app.repositories.turn_repo import TurnRepository
from app.core.auth import get_current_user_id

router = APIRouter(prefix="/sessions", tags=["sessions"])

@router.post("/", response_model=SessionResponse)
def create_session(session_data: SessionCreate, request: Request, db: Session = Depends(get_db)):
    repo = SessionRepository(db)
    session = repo.create(session_data, user_id=get_current_user_id(request))
    return session

@router.get("/", response_model=list[SessionResponse])
def list_sessions(
    request: Request,
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    user_id = get_current_user_id(request)
    return SessionRepository(db).list_recent(limit=limit, user_id=user_id)

@router.get("/{session_id}")
def get_session(session_id: str, request: Request, db: Session = Depends(get_db)):
    repo = SessionRepository(db)
    turn_repo = TurnRepository(db)
    session = repo.get(session_id, get_current_user_id(request))
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    turns = turn_repo.get_by_session(session_id)
    return {"session": session, "turns": turns}

@router.post("/{session_id}/finish", response_model=SessionResponse)
def finish_session(session_id: str, request: Request, db: Session = Depends(get_db)):
    repo = SessionRepository(db)
    session = repo.finish(session_id, get_current_user_id(request))
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session
