from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.mistake import MistakeResponse, MistakeResolveResponse
from app.repositories.mistake_repo import MistakeRepository
from app.core.auth import get_current_user_id, get_current_principal_id

router = APIRouter(prefix="/mistakes", tags=["mistakes"])

class MistakeReviewRequest(BaseModel):
    success: bool

@router.get("", response_model=list[MistakeResponse])
@router.get("/", response_model=list[MistakeResponse])
def get_mistakes(
    request: Request,
    limit: int = Query(50, ge=1, le=100),
    resolved: bool | None = None,
    db: Session = Depends(get_db)
):
    repo = MistakeRepository(db)
    return repo.list_mistakes(user_id=get_current_user_id(request), limit=limit, resolved=resolved, owner_user_id=get_current_principal_id(request))

@router.get("/frequent", response_model=list[MistakeResponse])
def get_frequent_mistakes(
    request: Request,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    repo = MistakeRepository(db)
    return repo.get_frequent_mistakes(user_id=get_current_user_id(request), limit=limit, owner_user_id=get_current_principal_id(request))

@router.post("/{mistake_id}/resolve", response_model=MistakeResolveResponse)
def resolve_mistake(
    mistake_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    repo = MistakeRepository(db)
    mistake = repo.resolve_mistake(mistake_id, get_current_user_id(request), get_current_principal_id(request))
    if not mistake:
        raise HTTPException(status_code=404, detail="Mistake not found")
    return MistakeResolveResponse(id=mistake.id, resolved=mistake.resolved)

@router.post("/{mistake_id}/review", response_model=MistakeResponse)
def review_mistake(mistake_id: str, data: MistakeReviewRequest, request: Request, db: Session = Depends(get_db)):
    mistake = MistakeRepository(db).review_mistake(
        mistake_id,
        get_current_user_id(request),
        get_current_principal_id(request),
        data.success,
    )
    if not mistake:
        raise HTTPException(status_code=404, detail="Mistake not found")
    return mistake
