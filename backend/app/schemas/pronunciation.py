from typing import List, Optional
from pydantic import BaseModel, Field

class WordPronunciation(BaseModel):
    word: str
    expected_ipa: str
    confidence: float = Field(..., ge=0.0, le=1.0, description="Acoustic / recognition confidence score")
    start: Optional[float] = None
    end: Optional[float] = None
    needs_review: bool = False
    syllables: List[str] = Field(default_factory=list)
    stress_index: Optional[int] = None
    feedback: Optional[str] = None

class RhythmMetrics(BaseModel):
    speech_rate_wpm: float
    pause_count: int
    pause_duration_ratio: float
    rhythm_consistency_score: float

class PronunciationAnalysisRequest(BaseModel):
    text: str
    session_id: Optional[str] = "default"
    audio_duration_ms: Optional[int] = None
    words: Optional[List[dict]] = None

class PronunciationReportResponse(BaseModel):
    overall_score: float = Field(..., description="Percentage score 0 - 100")
    estimated_band: float = Field(..., description="IELTS Pronunciation band 1.0 - 9.0")
    word_count: int
    words: List[WordPronunciation]
    problem_words: List[WordPronunciation]
    rhythm: RhythmMetrics
    feedback_summary: str
    disclaimer: str = "Acoustic assessment based on speech recognition confidence and phonetic alignment."

class PronunciationDrillRequest(BaseModel):
    target_word: str
    user_spoken_text: Optional[str] = None
    audio_confidence: Optional[float] = None

class PronunciationDrillResponse(BaseModel):
    word: str
    expected_ipa: str
    syllables: List[str]
    score: float
    accuracy: str
    tips: List[str]
    sample_sentence: str
