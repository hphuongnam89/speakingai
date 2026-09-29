from pydantic import BaseModel
from typing import Optional

class UserSettingsUpdate(BaseModel):
    correction_level: Optional[str] = None  # none, important, aggressive
    local_only: Optional[bool] = None
    cloud_fallback: Optional[bool] = None
    provider_preference: Optional[str] = None  # auto, local_only, cloud_only
    preferred_model: Optional[str] = None
    voice: Optional[str] = None

class UserSettingsResponse(BaseModel):
    user_id: str
    correction_level: str
    local_only: bool
    cloud_fallback: bool
    provider_preference: str = "auto"
    preferred_model: Optional[str] = None
    voice: str

    model_config = {"from_attributes": True}
