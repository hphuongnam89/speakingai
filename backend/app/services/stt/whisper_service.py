import logging
from importlib.util import find_spec
from typing import Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

class WhisperService:
    def __init__(self):
        self.model = None
        self.error = None
        try:
            from faster_whisper import WhisperModel
            self.model = WhisperModel(settings.WHISPER_MODEL, device="cpu", compute_type="int8")
        except ImportError:
            self.error = (
                "Speech recognition is unavailable because faster-whisper is not installed. "
                "Install backend dependencies with: pip install -r backend/requirements.txt"
            )
            logger.warning(self.error)
        except Exception as e:
            self.error = f"Could not load Whisper model '{settings.WHISPER_MODEL}': {e}"
            logger.error(f"Failed to load WhisperModel: {e}")

    @staticmethod
    def package_installed() -> bool:
        """Check installation without triggering a model download during page load."""
        try:
            return find_spec("faster_whisper") is not None
        except (ImportError, ValueError):
            return False

    def status(self) -> Dict[str, Any]:
        return {
            "available": self.model is not None,
            "package_installed": self.package_installed(),
            "model": settings.WHISPER_MODEL,
            "message": self.error,
        }

    def transcribe(self, audio_path: str) -> Dict[str, Any]:
        if not self.model:
            return {"error": self.error or "Whisper model is not available."}
        
        try:
            segments, info = self.model.transcribe(
                audio_path,
                beam_size=5,
                word_timestamps=True,
            )
            segments_list = list(segments)
            
            text = "".join([segment.text for segment in segments_list])
            duration_ms = int(round(info.duration * 1000))
            
            return {
                "text": text,
                "duration_ms": duration_ms,
                "language": info.language,
                "segments": [
                    {
                        "start": s.start,
                        "end": s.end,
                        "text": s.text,
                        "words": [
                            {
                                "word": w.word,
                                "start": w.start,
                                "end": w.end,
                                "probability": w.probability,
                            }
                            for w in s.words
                        ] if s.words else []
                    } for s in segments_list
                ]
            }
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return {"error": f"Whisper transcription failed: {e}"}

    def calculate_metrics(self, segments: list, text: str, duration_ms: float) -> Dict[str, Any]:
        speaking_duration_ms = 0
        long_pauses = 0
        filler_count = 0
        fillers = {'um', 'uh', 'hmm', 'like', 'you know', 'basically', 'actually'}
        
        last_end = 0
        for i, segment in enumerate(segments):
            speaking_duration_ms += (segment['end'] - segment['start']) * 1000
            if i > 0:
                pause = segment['start'] - last_end
                if pause > 1.5:
                    long_pauses += 1
            last_end = segment['end']
            
        words = [w.strip(".,!?").lower() for w in text.split()]
        word_count = len(words)
        
        text_lower = text.lower()
        for filler in fillers:
            if " " in filler:
                filler_count += text_lower.count(filler)
            else:
                filler_count += words.count(filler)
                
        speaking_duration_s = speaking_duration_ms / 1000
        wpm = (word_count / (speaking_duration_s / 60)) if speaking_duration_s > 0 else 0
        
        return {
            "wpm": wpm,
            "long_pauses": long_pauses,
            "total_duration_ms": int(round(duration_ms)),
            "speaking_duration_ms": int(round(speaking_duration_ms)),
            "filler_count": filler_count
        }

_whisper_service = None

def get_whisper_service() -> WhisperService:
    global _whisper_service
    if _whisper_service is None:
        _whisper_service = WhisperService()
    return _whisper_service


def get_whisper_status() -> Dict[str, Any]:
    """Inspect readiness without constructing WhisperModel or downloading weights."""
    if _whisper_service is not None:
        return _whisper_service.status()

    package_installed = WhisperService.package_installed()
    return {
        "available": False,
        "package_installed": package_installed,
        "model": settings.WHISPER_MODEL,
        "message": (
            "Whisper sẽ tải model khi bạn ghi âm lần đầu."
            if package_installed
            else "Whisper chưa sẵn sàng: backend hiện thiếu faster-whisper. "
            "Cài dependency từ thư mục dự án: pip install -r backend/requirements.txt"
        ),
    }
