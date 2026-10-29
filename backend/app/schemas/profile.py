from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class ProfileCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    target_band: float = Field(7.0, ge=4.0, le=9.0)
    daily_target_minutes: int = Field(20, ge=5, le=300)
    target_duration_months: int = Field(3, ge=1, le=24)
    avatar_color: Optional[str] = "#4f46e5"


class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    target_band: Optional[float] = Field(None, ge=4.0, le=9.0)
    daily_target_minutes: Optional[int] = Field(None, ge=5, le=300)
    target_duration_months: Optional[int] = Field(None, ge=1, le=24)
    roadmap_data: Optional[Dict[str, Any]] = None


class ProfileResponse(BaseModel):
    id: str
    name: str
    avatar_color: str
    current_band: Optional[float] = None
    target_band: float
    daily_target_minutes: int
    target_duration_months: int
    placement_status: str
    roadmap_data: Optional[Dict[str, Any]] = None
    is_active: bool
    today_speaking_minutes: float = 0.0
    streak_days: int = 0
    total_sessions: int = 0
    created_at: datetime
    last_active_at: datetime

    model_config = {"from_attributes": True}
