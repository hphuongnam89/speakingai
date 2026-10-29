from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MistakeResponse(BaseModel):
    id: str
    user_id: str
    session_id: Optional[str] = None
    turn_id: Optional[str] = None
    category: str
    error_type: str = "grammar"
    subtype: str = "general"
    original_text: str
    corrected_text: str
    explanation: Optional[str] = None
    severity: int
    first_seen_at: datetime
    last_seen_at: datetime
    occurrence_count: int
    resolved: bool
    successful_reuse_count: int = 0
    next_review_at: Optional[datetime] = None
    last_reviewed_at: Optional[datetime] = None
    mastery_state: str = "learning"
    example_sentence: Optional[str] = None

    model_config = {"from_attributes": True}

class MistakeResolveResponse(BaseModel):
    id: str
    resolved: bool
