from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional, List

class CueCard(BaseModel):
    id: str
    topic: str
    title: str
    bullets: List[str]
    follow_up: Optional[str] = None
    part_3_questions: Optional[List[str]] = None

class IeltsStartRequest(BaseModel):
    part: str = Field(default="part1", max_length=50)
    topic: Optional[str] = Field(default=None, max_length=2000)

class IeltsStartResponse(BaseModel):
    session_id: str
    part: str
    cue_card: Optional[CueCard] = None
    greeting: str
    question: str

class IeltsRespondRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=128)
    user_text: str = Field(min_length=1, max_length=12000)
    part: str = Field(default="part1", max_length=50)

class IeltsRespondResponse(BaseModel):
    message: str
    tts_text: str
    is_completed: bool = False
    next_part: Optional[str] = None
    cue_card: Optional[CueCard] = None
    timing_warning: Optional[str] = None

class SuggestedExpression(BaseModel):
    original: str
    upgraded: str
    context: Optional[str] = None

class IeltsEvaluationResponse(BaseModel):
    session_id: str
    overall_band: Optional[float] = None
    fluency_score: Optional[float] = None
    fluency_feedback: str
    lexical_score: Optional[float] = None
    lexical_feedback: str
    grammar_score: Optional[float] = None
    grammar_feedback: str
    pronunciation_score: Optional[float] = None
    strengths: List[str] = []
    areas_for_improvement: List[str] = []
    suggested_expressions: List[SuggestedExpression] = []
    examiner_summary: str
    disclaimer: str = "Estimated score — not an official IELTS result."
    score_status: str = "provisional"
    calibration_status: str = "unverified"
    confidence: Optional[float] = None
    confidence_range: str = "insufficient calibration data"
    limitation: str = "Pronunciation is not scored from transcript alone."
    scoring_version: str = "phase8-v1"
    model_id: Optional[str] = None
    prompt_version: str = "ielts-evaluation-v1"
    provider: Optional[str] = None
    evidence_words: int = 0

class EvaluationFeedbackRequest(BaseModel):
    flag: str = Field(min_length=1, max_length=50)
    comment: Optional[str] = Field(default=None, max_length=2000)

class CalibrationSampleRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    sample_key: str = Field(min_length=1, max_length=100, pattern=r"^[a-zA-Z0-9_-]+$")
    level: str = Field(default="unknown", max_length=50)
    transcript: str = Field(min_length=1, max_length=20000)
    human_fc: Optional[float] = Field(default=None, ge=1, le=9)
    human_lr: Optional[float] = Field(default=None, ge=1, le=9)
    human_gra: Optional[float] = Field(default=None, ge=1, le=9)
    human_pronunciation: Optional[float] = Field(default=None, ge=1, le=9)
    ai_payload_json: Optional[str] = Field(default=None, max_length=30000)
    consented: bool = False

    @field_validator("ai_payload_json")
    @classmethod
    def valid_payload(cls, value):
        if value is not None:
            import json
            def reject_constant(value):
                raise ValueError("Non-finite values are not accepted")
            try:
                parsed = json.loads(value, parse_constant=reject_constant)
            except RecursionError as exc:
                raise ValueError("AI payload is nested too deeply") from exc
            if not isinstance(parsed, dict):
                raise ValueError("AI payload must be an object")
        return value
