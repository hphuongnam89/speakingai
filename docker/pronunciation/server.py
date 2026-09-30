import logging
import os
import tempfile

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from openpronounce import audio, speech

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("pronunciation-assessor")
app = FastAPI(title="IELTS pronunciation assessor", docs_url=None, redoc_url=None)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/pronunciation")
def assess_pronunciation(
    file: UploadFile = File(...),
    expected_text: str = Form(..., min_length=1, max_length=5000),
    lang: str = Form("en"),
):
    if lang != "en":
        raise HTTPException(status_code=422, detail="Pronunciation scoring is currently calibrated for English only")

    suffix = os.path.splitext(file.filename or "recording.m4a")[1] or ".m4a"
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix) as audio_file:
            audio_file.write(file.file.read())
            audio_file.flush()
            waveform = audio.load(audio_file.name)
            result = speech.compare_audio_with_text(waveform, expected_text, lang="en")
    except Exception as exc:
        logger.exception("Pronunciation analysis failed")
        raise HTTPException(status_code=503, detail="Pronunciation model could not analyze this recording") from exc

    differences = result.get("differences") or {}
    return {
        "score": result.get("score"),
        "differences": {
            "errors": [
                {
                    "word": error.get("word", ""),
                    "expected": error.get("expected", ""),
                    "actual": error.get("actual", ""),
                    "confidence": error.get("confidence"),
                }
                for error in differences.get("errors", [])
            ]
        },
    }
