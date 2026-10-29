from pydantic import BaseModel
from typing import Optional
from app.schemas.pronunciation import PronunciationReportResponse

class Correction(BaseModel):
    original: str
    corrected: str
    explanation: str
    category: str = "grammar"
    error_type: str = "grammar"
    subtype: str = "general"
    severity: str = "important"
    practice_prompt: str = "Say the corrected sentence in your own words."
    should_repeat: bool = False

class ConversationRequest(BaseModel):
    session_id: str
    user_text: str
    mode: str = "daily"
    correction_level: Optional[str] = None  # none, important, aggressive
    request_id: Optional[str] = None  # Idempotency token to prevent duplicate turns

class RepeatCheckRequest(BaseModel):
    expected_text: str
    actual_text: str

class RepeatCheckResponse(BaseModel):
    passed: bool
    similarity: float
    feedback: str

class ConversationResponse(BaseModel):
    message: str
    corrections: list[Correction] = []
    upgraded_sentence: Optional[str] = None
    session_focus: Optional[str] = None
    self_assessment_prompt: Optional[str] = "What is one sentence pattern you can reuse today?"
    repeat_prompt: Optional[str] = None
    tts_text: str = ""
    turn_id: Optional[str] = None
    pronunciation: Optional[PronunciationReportResponse] = None
    provider_used: Optional[str] = None
    fallback_triggered: Optional[bool] = False
    latency_ms: Optional[float] = None
