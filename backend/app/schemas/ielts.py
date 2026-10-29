from pydantic import BaseModel
from typing import Optional, List

class CueCard(BaseModel):
    id: str
    topic: str
    title: str
    bullets: List[str]
    follow_up: Optional[str] = None
    part_3_questions: Optional[List[str]] = None

class IeltsStartRequest(BaseModel):
    part: str = "part1"  # "part1", "part2", "part3", "full_mock"
    topic: Optional[str] = None

class IeltsStartResponse(BaseModel):
    session_id: str
    part: str
    cue_card: Optional[CueCard] = None
    greeting: str
    question: str

class IeltsRespondRequest(BaseModel):
    session_id: str
    user_text: str
    part: str = "part1"

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
    overall_band: float
    fluency_score: float
    fluency_feedback: str
    lexical_score: float
    lexical_feedback: str
    grammar_score: float
    grammar_feedback: str
    pronunciation_score: Optional[float] = None
    strengths: List[str] = []
    areas_for_improvement: List[str] = []
    suggested_expressions: List[SuggestedExpression] = []
    examiner_summary: str
    disclaimer: str = "Estimated score — not an official IELTS result."
    score_status: str = "provisional"
    confidence: float = 0.0
    confidence_range: str = "insufficient calibration data"
    limitation: str = "Pronunciation is not scored from transcript alone."
    scoring_version: str = "phase8-v1"
    model_id: Optional[str] = None
    prompt_version: str = "ielts-evaluation-v1"

class EvaluationFeedbackRequest(BaseModel):
    flag: str
    comment: Optional[str] = None
