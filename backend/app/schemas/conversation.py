from pydantic import BaseModel
from typing import Optional
from app.schemas.pronunciation import PronunciationReportResponse

class Correction(BaseModel):
    original: str
    corrected: str
    explanation: str
    category: str = "grammar"
    should_repeat: bool = False

class ConversationRequest(BaseModel):
    session_id: str
    user_text: str
    mode: str = "daily"
    correction_level: Optional[str] = None  # none, important, aggressive

class ConversationResponse(BaseModel):
    message: str
    corrections: list[Correction] = []
    repeat_prompt: Optional[str] = None
    tts_text: str = ""
    turn_id: Optional[str] = None
    pronunciation: Optional[PronunciationReportResponse] = None
    provider_used: Optional[str] = None
    fallback_triggered: Optional[bool] = False
    latency_ms: Optional[float] = None
