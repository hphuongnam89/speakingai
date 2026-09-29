from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MistakeResponse(BaseModel):
    id: str
    user_id: str
    session_id: Optional[str] = None
    turn_id: Optional[str] = None
    category: str
    original_text: str
    corrected_text: str
    explanation: Optional[str] = None
    severity: int
    first_seen_at: datetime
    last_seen_at: datetime
    occurrence_count: int
    resolved: bool

    model_config = {"from_attributes": True}

class MistakeResolveResponse(BaseModel):
    id: str
    resolved: bool
