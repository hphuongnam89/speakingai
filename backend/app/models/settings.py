from sqlalchemy import Column, String, Boolean
from app.core.database import Base

class UserSettingsModel(Base):
    __tablename__ = "user_settings"

    user_id = Column(String, primary_key=True, default="default")
    correction_level = Column(String, default="important")  # none, important, aggressive
    local_only = Column(Boolean, default=True)
    cloud_fallback = Column(Boolean, default=False)
    provider_preference = Column(String, default="auto")  # auto, local_only, cloud_only
    preferred_model = Column(String, nullable=True)
    voice = Column(String, default="default")
