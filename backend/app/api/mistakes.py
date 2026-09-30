from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.mistake import MistakeResponse, MistakeResolveResponse
from app.repositories.mistake_repo import MistakeRepository
from app.core.auth import get_current_user_id

router = APIRouter(prefix="/mistakes", tags=["mistakes"])

@router.get("", response_model=list[MistakeResponse])
@router.get("/", response_model=list[MistakeResponse])
def get_mistakes(
    request: Request,
    limit: int = Query(50, ge=1, le=100),
    resolved: bool | None = None,
    db: Session = Depends(get_db)
):
    repo = MistakeRepository(db)
    return repo.list_mistakes(user_id=get_current_user_id(request), limit=limit, resolved=resolved)

@router.get("/frequent", response_model=list[MistakeResponse])
def get_frequent_mistakes(
    request: Request,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    repo = MistakeRepository(db)
    return repo.get_frequent_mistakes(user_id=get_current_user_id(request), limit=limit)

@router.post("/{mistake_id}/resolve", response_model=MistakeResolveResponse)
def resolve_mistake(
    mistake_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    repo = MistakeRepository(db)
    mistake = repo.resolve_mistake(mistake_id, get_current_user_id(request))
    if not mistake:
        raise HTTPException(status_code=404, detail="Mistake not found")
    return MistakeResolveResponse(id=mistake.id, resolved=mistake.resolved)
