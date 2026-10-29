import os
import sys
import logging
from importlib.util import find_spec
from typing import Dict, Any
from app.core.config import settings

# Ensure CUDA runtime DLLs (cublas64_12.dll, etc.) are found on Windows
try:
    import ctranslate2
    ct2_dir = os.path.dirname(ctranslate2.__file__)
    if hasattr(os, "add_dll_directory") and os.path.exists(ct2_dir):
        os.add_dll_directory(ct2_dir)
    if ct2_dir not in os.environ.get("PATH", ""):
        os.environ["PATH"] = ct2_dir + ";" + os.environ.get("PATH", "")
except Exception:
    pass

logger = logging.getLogger(__name__)

class WhisperService:
    def __init__(self):
        self.model = None
        self.error = None
        self.device = "cpu"
        self.compute_type = "int8"
        try:
            import ctranslate2
            from faster_whisper import WhisperModel
            
            pref_device = (getattr(settings, "WHISPER_DEVICE", "auto") or "auto").lower()
            if pref_device == "cuda" or (pref_device == "auto" and ctranslate2.get_cuda_device_count() > 0):
                self.device = "cuda"
                self.compute_type = "float16" if getattr(settings, "WHISPER_COMPUTE_TYPE", "auto") in {"auto", "float16"} else settings.WHISPER_COMPUTE_TYPE
            else:
                self.device = "cpu"
                self.compute_type = "int8" if getattr(settings, "WHISPER_COMPUTE_TYPE", "auto") in {"auto", "int8"} else settings.WHISPER_COMPUTE_TYPE

            logger.info(f"Initializing WhisperModel: model={settings.WHISPER_MODEL}, device={self.device}, compute_type={self.compute_type}")
            self.model = WhisperModel(settings.WHISPER_MODEL, device=self.device, compute_type=self.compute_type)
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
            "device": self.device,
            "compute_type": self.compute_type,
            "message": self.error,
        }

    def transcribe(self, audio_path: str, initial_prompt: str | None = None) -> Dict[str, Any]:
        if not self.model:
            return {"error": self.error or "Whisper model is not available."}
        
        try:
            prompt = initial_prompt or (
                "IELTS Speaking examination practice test. The candidate answers English test questions with natural accent. "
                "Transcribe accurately with standard English spelling, academic vocabulary, and correct punctuation."
            )
            segments, info = self.model.transcribe(
                audio_path,
                beam_size=5,
                language="en",
                initial_prompt=prompt,
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=400),
                condition_on_previous_text=False,
                temperature=0.0,
                word_timestamps=True,
            )
            segments_list = list(segments)
            
            text = " ".join([segment.text.strip() for segment in segments_list]).strip()
            duration_ms = int(round(info.duration * 1000))
            
            return {
                "text": text,
                "duration_ms": duration_ms,
                "language": info.language,
                "segments": [
                    {
                        "start": s.start,
                        "end": s.end,
                        "text": s.text.strip(),
                        "words": [
                            {
                                "word": w.word.strip(),
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
            err_msg = str(e).lower()
            if self.device == "cuda" and ("cublas" in err_msg or "cuda" in err_msg or "dll" in err_msg):
                logger.warning(f"CUDA transcription failed ({e}), automatically falling back to CPU...")
                try:
                    from faster_whisper import WhisperModel
                    self.device = "cpu"
                    self.compute_type = "int8"
                    self.model = WhisperModel(settings.WHISPER_MODEL, device="cpu", compute_type="int8")
                    return self.transcribe(audio_path, initial_prompt)
                except Exception as cpu_err:
                    logger.error(f"CPU fallback also failed: {cpu_err}")
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
        "device": getattr(settings, "WHISPER_DEVICE", "auto"),
        "compute_type": getattr(settings, "WHISPER_COMPUTE_TYPE", "auto"),
        "message": (
            "Whisper sẽ tải model khi bạn ghi âm lần đầu."
            if package_installed
            else "Whisper chưa sẵn sàng: backend hiện thiếu faster-whisper. "
            "Cài dependency từ thư mục dự án: pip install -r backend/requirements.txt"
        ),
    }
