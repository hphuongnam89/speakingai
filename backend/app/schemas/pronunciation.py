from typing import List, Optional
from pydantic import BaseModel, Field

class WordPronunciation(BaseModel):
    word: str
    expected_ipa: str
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Whisper speech-recognition confidence; not a pronunciation score")
    start: Optional[float] = None
    end: Optional[float] = None
    needs_review: bool = False
    syllables: List[str] = Field(default_factory=list)
    stress_index: Optional[int] = None
    feedback: Optional[str] = None

class RhythmMetrics(BaseModel):
    speech_rate_wpm: Optional[float] = None
    pause_count: Optional[int] = None
    pause_duration_ratio: Optional[float] = None
    rhythm_consistency_score: Optional[float] = None

class PronunciationAnalysisRequest(BaseModel):
    text: str
    session_id: Optional[str] = "default"
    audio_duration_ms: Optional[int] = None
    words: Optional[List[dict]] = None

class PronunciationError(BaseModel):
    word: str
    expected_ipa: str
    heard_ipa: str
    confidence: Optional[float] = None

class PronunciationReportResponse(BaseModel):
    recognition_confidence: Optional[float] = Field(None, description="Mean Whisper recognition confidence percentage, not a pronunciation score")
    pronunciation_score: Optional[float] = Field(None, ge=0.0, le=100.0, description="Experimental audio-based score; not an IELTS band")
    pronunciation_errors: List[PronunciationError] = Field(default_factory=list)
    scorer: Optional[str] = None
    word_count: int
    words: List[WordPronunciation]
    problem_words: List[WordPronunciation]
    rhythm: RhythmMetrics
    feedback_summary: str
    disclaimer: str = "Whisper confidence is not pronunciation accuracy. The optional OpenPronounce score is experimental, English-focused, and is not an IELTS result."

class PronunciationDrillRequest(BaseModel):
    target_word: str

class PronunciationDrillResponse(BaseModel):
    word: str
    expected_ipa: str
    syllables: List[str]
    score: Optional[float] = None
    accuracy: str
    tips: List[str]
    sample_sentence: str
