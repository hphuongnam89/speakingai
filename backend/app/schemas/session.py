from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SessionCreate(BaseModel):
    mode: str
    topic: Optional[str] = None

class SessionResponse(BaseModel):
    id: str
    mode: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    topic: Optional[str] = None
    total_speaking_ms: int = 0
    provider: Optional[str] = None

    model_config = {"from_attributes": True}

class SessionDetail(SessionResponse):
    turns: list = []
