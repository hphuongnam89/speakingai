import re
import logging
import mimetypes
import os
from typing import List, Dict, Any, Optional
import httpx
from app.core.config import settings
from app.services.pronunciation.phonetic_dict import get_phonetic_info
from app.schemas.pronunciation import (
    WordPronunciation,
    RhythmMetrics,
    PronunciationReportResponse,
    PronunciationDrillResponse,
    PronunciationError,
)

logger = logging.getLogger(__name__)

class PronunciationService:
    """
    Summarizes Whisper word confidence and timing. This is not a pronunciation scorer.
    """

    def analyze_speech(
        self,
        text: str,
        segments: Optional[List[Dict[str, Any]]] = None,
        words_data: Optional[List[Dict[str, Any]]] = None,
        duration_ms: float = 0.0,
        audio_path: Optional[str] = None,
    ) -> PronunciationReportResponse:
        raw_words = re.findall(r"\b[A-Za-z'-]+\b", text)
        if not raw_words:
            return PronunciationReportResponse(
                recognition_confidence=None,
                word_count=0,
                words=[],
                problem_words=[],
                rhythm=RhythmMetrics(
                    speech_rate_wpm=None,
                    pause_count=None,
                    pause_duration_ratio=None,
                    rhythm_consistency_score=None
                ),
                feedback_summary="No spoken words were detected."
            )

        word_results: List[WordPronunciation] = []
        problem_words: List[WordPronunciation] = []

        # Map whisper words if present
        whisper_map: Dict[str, List[Dict[str, Any]]] = {}
        if words_data:
            for w_item in words_data:
                clean_w = re.sub(r"[^A-Za-z]", "", w_item.get("word", "")).lower()
                if clean_w:
                    whisper_map.setdefault(clean_w, []).append(w_item)

        observed_confidences: List[float] = []
        seen_word_counts: Dict[str, int] = {}

        for word in raw_words:
            clean_word = word.lower()
            info = get_phonetic_info(clean_word)

            start = None
            end = None
            conf = None

            # Check if whisper acoustic timestamp and probability exist
            word_matches = whisper_map.get(clean_word, [])
            match_index = seen_word_counts.get(clean_word, 0)
            seen_word_counts[clean_word] = match_index + 1
            if match_index < len(word_matches):
                w_match = word_matches[match_index]
                start = w_match.get("start")
                end = w_match.get("end")
                probability = w_match.get("probability")
                if probability is not None:
                    conf = max(0.0, min(1.0, round(float(probability), 2)))
                    observed_confidences.append(conf)

            # Words requiring attention (threshold 0.80)
            needs_review = conf is not None and conf < 0.80

            wp = WordPronunciation(
                word=word,
                expected_ipa=info["expected_ipa"],
                confidence=conf,
                start=start,
                end=end,
                needs_review=needs_review,
                syllables=info["syllables"],
                stress_index=info["stress_index"],
                feedback=("Whisper was uncertain about this word; check the transcript." if needs_review else None)
            )

            word_results.append(wp)
            if needs_review:
                problem_words.append(wp)

        # Rhythm & Pauses computation
        pause_count = 0
        total_pause_ms = 0.0
        if segments and len(segments) > 1:
            last_end = 0.0
            for seg in segments:
                s_start = seg.get("start", 0.0) * 1000
                s_end = seg.get("end", 0.0) * 1000
                if last_end > 0.0:
                    gap = s_start - last_end
                    if gap > 700: # gap > 0.7s counts as deliberate pause
                        pause_count += 1
                        total_pause_ms += gap
                last_end = s_end

        has_audio_duration = duration_ms > 0
        pause_ratio = round(total_pause_ms / duration_ms, 2) if has_audio_duration else None
        duration_s = duration_ms / 1000.0
        wpm = round((len(raw_words) / (duration_s / 60.0)), 1) if has_audio_duration else None

        rhythm_metrics = RhythmMetrics(
            speech_rate_wpm=wpm,
            pause_count=pause_count if has_audio_duration else None,
            pause_duration_ratio=pause_ratio,
            rhythm_consistency_score=None
        )

        assessment = self._assess_audio(audio_path, text) if audio_path else None
        pronunciation_errors: List[PronunciationError] = []
        pronunciation_score = None
        scorer = None
        if assessment:
            differences = assessment.get("differences") or {}
            for error in differences.get("errors", []):
                word_name = str(error.get("word", "")).strip()
                if not word_name:
                    continue
                raw_confidence = error.get("confidence")
                confidence = float(raw_confidence) if raw_confidence is not None else None
                if confidence is not None and confidence > 1:
                    confidence /= 100
                pronunciation_errors.append(PronunciationError(
                    word=word_name,
                    expected_ipa=str(error.get("expected", "")),
                    heard_ipa=str(error.get("actual", "")),
                    confidence=confidence,
                ))
            raw_score = assessment.get("score")
            if raw_score is not None:
                pronunciation_score = max(0.0, min(100.0, float(raw_score)))
                scorer = "OpenPronounce 0.3.0 (experimental)"

            error_words = {item.word.casefold() for item in pronunciation_errors}
            if error_words:
                for word_result in word_results:
                    if word_result.word.casefold() in error_words:
                        word_result.needs_review = True
                        matched = next(item for item in pronunciation_errors if item.word.casefold() == word_result.word.casefold())
                        word_result.feedback = f"Possible sound difference: expected /{matched.expected_ipa}/, heard /{matched.heard_ipa}/."
                problem_words = [word for word in word_results if word.needs_review]

        # Whisper confidence reflects recognition certainty, not pronunciation quality.
        mean_confidence = (
            round(sum(observed_confidences) / len(observed_confidences) * 100, 1)
            if observed_confidences else None
        )
        if observed_confidences:
            summary = "Whisper recognition confidence is shown for each word. Low confidence can indicate an unclear recording or an uncertain transcript; it is not a pronunciation score."
        else:
            summary = "Whisper did not return word confidence data. Pronunciation cannot be scored from transcript text alone."
        if pronunciation_score is not None:
            summary += " An experimental English audio-based pronunciation estimate is also available; it is not an IELTS band."

        return PronunciationReportResponse(
            recognition_confidence=mean_confidence,
            pronunciation_score=pronunciation_score,
            pronunciation_errors=pronunciation_errors,
            scorer=scorer,
            word_count=len(raw_words),
            words=word_results,
            problem_words=problem_words,
            rhythm=rhythm_metrics,
            feedback_summary=summary
        )

    @staticmethod
    def _assess_audio(audio_path: str, text: str) -> Optional[dict]:
        assessor_url = settings.PRONUNCIATION_ASSESSOR_URL.strip().rstrip("/")
        if not assessor_url:
            return None
        try:
            with open(audio_path, "rb") as audio_file:
                response = httpx.post(
                    f"{assessor_url}/pronunciation",
                    files={
                        "file": (
                            os.path.basename(audio_path),
                            audio_file,
                            mimetypes.guess_type(audio_path)[0] or "application/octet-stream",
                        )
                    },
                    data={"expected_text": text, "lang": "en"},
                    timeout=httpx.Timeout(settings.PRONUNCIATION_ASSESSOR_TIMEOUT, connect=10.0),
                )
            response.raise_for_status()
            return response.json()
        except (OSError, httpx.HTTPError, ValueError) as exc:
            logger.warning("Audio pronunciation assessor unavailable: %s", exc)
            return None

    def evaluate_drill(
        self,
        target_word: str
    ) -> PronunciationDrillResponse:
        clean_target = target_word.strip().lower()
        info = get_phonetic_info(clean_target)

        tips = [
            f"Expected IPA: {info['expected_ipa']}",
            f"Syllable breakdown: {' - '.join(info['syllables'])} (Stress: {info['syllables'][info['stress_index']].upper() if info['stress_index'] < len(info['syllables']) else ''})",
            info["feedback"],
            "Practice feedback is not scored because this service does not yet analyze the recorded audio acoustically."
        ]

        sample_sentence = f"I really {clean_target} the opportunity to practice English."
        if clean_target == "enjoyed":
            sample_sentence = "I thoroughly enjoyed visiting the ancient coastal town."
        elif clean_target == "technology":
            sample_sentence = "Modern technology has revolutionized daily communication."

        return PronunciationDrillResponse(
            word=target_word,
            expected_ipa=info["expected_ipa"],
            syllables=info["syllables"],
            score=None,
            accuracy="Not scored",
            tips=tips,
            sample_sentence=sample_sentence
        )

_pronunciation_service = None

def get_pronunciation_service() -> PronunciationService:
    global _pronunciation_service
    if _pronunciation_service is None:
        _pronunciation_service = PronunciationService()
    return _pronunciation_service
