from pydantic import BaseModel
from typing import Optional, List

class ProgressSummaryResponse(BaseModel):
    streak: int
    total_speaking_minutes: float
    total_sessions: int
    avg_wpm: float
    latest_band: Optional[float] = None
    total_mistakes: int

class DailyStatItem(BaseModel):
    date: str
    day_of_week: str
    speaking_minutes: float
    session_count: int
    mistake_count: int

class AdaptivePlanResponse(BaseModel):
    today_objective: str
    top_weaknesses: List[str]
    recommended_topic: str
    challenge_phrases: List[str]
