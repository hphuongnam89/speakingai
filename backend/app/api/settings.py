from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.settings import UserSettingsResponse, UserSettingsUpdate
from app.repositories.settings_repo import SettingsRepository

router = APIRouter(prefix="/settings", tags=["settings"])

@router.get("", response_model=UserSettingsResponse)
@router.get("/", response_model=UserSettingsResponse)
def get_settings(user_id: str = "default", db: Session = Depends(get_db)):
    repo = SettingsRepository(db)
    return repo.get_or_create(user_id=user_id)

@router.put("", response_model=UserSettingsResponse)
@router.put("/", response_model=UserSettingsResponse)
def update_settings(update_data: UserSettingsUpdate, user_id: str = "default", db: Session = Depends(get_db)):
    repo = SettingsRepository(db)
    return repo.update(user_id=user_id, **update_data.model_dump(exclude_unset=True))
