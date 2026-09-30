from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.settings import UserSettingsResponse, UserSettingsUpdate
from app.repositories.settings_repo import SettingsRepository
from app.core.auth import get_current_user_id

router = APIRouter(prefix="/settings", tags=["settings"])

@router.get("", response_model=UserSettingsResponse)
@router.get("/", response_model=UserSettingsResponse)
def get_settings(request: Request, db: Session = Depends(get_db)):
    repo = SettingsRepository(db)
    return repo.get_or_create(user_id=get_current_user_id(request))

@router.put("", response_model=UserSettingsResponse)
@router.put("/", response_model=UserSettingsResponse)
def update_settings(update_data: UserSettingsUpdate, request: Request, db: Session = Depends(get_db)):
    repo = SettingsRepository(db)
    return repo.update(user_id=get_current_user_id(request), **update_data.model_dump(exclude_unset=True))
