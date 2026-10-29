from pydantic import BaseModel, Field
from typing import Optional

class PilotStartRequest(BaseModel):
    participant_code: str = Field(min_length=3, max_length=40, pattern=r"^[A-Za-z0-9_-]+$")
    consent_audio: bool
    consent_feedback: bool

class PilotStartResponse(BaseModel):
    pilot_run_id: str
    status: str
    audio_recording_allowed: bool

class PilotEventRequest(BaseModel):
    task_key: str = Field(min_length=2, max_length=80)
    outcome: str
    help_used: bool = False
    understood_quote: Optional[str] = Field(default=None, max_length=500)

class PilotFeedbackRequest(BaseModel):
    next_action_clear: int = Field(ge=1, le=5)
    correction_useful: int = Field(ge=1, le=5)
    score_too_certain: int = Field(ge=1, le=5)
    would_return: int = Field(ge=1, le=5)
    free_text: Optional[str] = Field(default=None, max_length=2000)

class PilotSummaryResponse(BaseModel):
    pilot_run_id: str
    event_count: int
    completed_without_help: int
    completed_with_help: int
    blocked: int
    completion_rate: float
    feedback_submitted: bool
