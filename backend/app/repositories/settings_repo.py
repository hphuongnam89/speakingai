from sqlalchemy.orm import Session
from app.models.settings import UserSettingsModel

class SettingsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create(self, user_id: str = "default") -> UserSettingsModel:
        settings = self.db.query(UserSettingsModel).filter(UserSettingsModel.user_id == user_id).first()
        if not settings:
            settings = UserSettingsModel(
                user_id=user_id,
                correction_level="important",
                local_only=True,
                cloud_fallback=False,
                voice="default"
            )
            self.db.add(settings)
            self.db.commit()
            self.db.refresh(settings)
        return settings

    def update(self, user_id: str = "default", **kwargs) -> UserSettingsModel:
        settings = self.get_or_create(user_id)
        for key, value in kwargs.items():
            if value is not None and hasattr(settings, key):
                setattr(settings, key, value)
        self.db.commit()
        self.db.refresh(settings)
        return settings
