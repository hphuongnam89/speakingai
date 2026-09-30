from fastapi import APIRouter, HTTPException, Depends
from app.services.pronunciation.pronunciation_service import get_pronunciation_service
from app.services.pronunciation.phonetic_dict import get_phonetic_info
from app.schemas.pronunciation import (
    PronunciationAnalysisRequest,
    PronunciationReportResponse,
    PronunciationDrillRequest,
    PronunciationDrillResponse
)

router = APIRouter(prefix="/pronunciation", tags=["pronunciation"])

@router.post("/analyze", response_model=PronunciationReportResponse)
def analyze_pronunciation(request: PronunciationAnalysisRequest):
    service = get_pronunciation_service()
    report = service.analyze_speech(
        text=request.text,
        words_data=request.words,
        duration_ms=float(request.audio_duration_ms or 0)
    )
    return report

@router.get("/dictionary/{word}")
def get_word_phonetics(word: str):
    info = get_phonetic_info(word)
    return info

@router.post("/drill", response_model=PronunciationDrillResponse)
def evaluate_drill(request: PronunciationDrillRequest):
    service = get_pronunciation_service()
    res = service.evaluate_drill(
        target_word=request.target_word
    )
    return res
