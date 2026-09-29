from pydantic import BaseModel

class AudioMetrics(BaseModel):
    wpm: float
    long_pauses: int
    total_duration_ms: int
    speaking_duration_ms: int
    filler_count: int

class TranscribeResponse(BaseModel):
    text: str
    duration_ms: int
    language: str = "en"
    metrics: AudioMetrics
    turn_id: str | None = None
