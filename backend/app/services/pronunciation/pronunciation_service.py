import re
import math
from typing import List, Dict, Any, Optional
from app.services.pronunciation.phonetic_dict import get_phonetic_info
from app.schemas.pronunciation import (
    WordPronunciation,
    RhythmMetrics,
    PronunciationReportResponse,
    PronunciationDrillResponse
)

class PronunciationService:
    """
    Core engine for acoustic pronunciation scoring, phoneme alignment,
    rhythm analysis, and interactive pronunciation drills.
    """

    def analyze_speech(
        self,
        text: str,
        segments: Optional[List[Dict[str, Any]]] = None,
        words_data: Optional[List[Dict[str, Any]]] = None,
        duration_ms: float = 0.0
    ) -> PronunciationReportResponse:
        raw_words = re.findall(r"\b[A-Za-z'-]+\b", text)
        if not raw_words:
            return PronunciationReportResponse(
                overall_score=0.0,
                estimated_band=1.0,
                word_count=0,
                words=[],
                problem_words=[],
                rhythm=RhythmMetrics(
                    speech_rate_wpm=0.0,
                    pause_count=0,
                    pause_duration_ratio=0.0,
                    rhythm_consistency_score=0.0
                ),
                feedback_summary="No spoken words detected for pronunciation analysis."
            )

        word_results: List[WordPronunciation] = []
        problem_words: List[WordPronunciation] = []

        # Map whisper words if present
        whisper_map: Dict[str, Dict[str, Any]] = {}
        if words_data:
            for w_item in words_data:
                clean_w = re.sub(r"[^A-Za-z]", "", w_item.get("word", "")).lower()
                if clean_w and clean_w not in whisper_map:
                    whisper_map[clean_w] = w_item

        total_confidence = 0.0

        for i, word in enumerate(raw_words):
            clean_word = word.lower()
            info = get_phonetic_info(clean_word)

            start = None
            end = None
            conf = 0.88 # default baseline for recognized speech

            # Check if whisper acoustic timestamp and probability exist
            if clean_word in whisper_map:
                w_match = whisper_map[clean_word]
                start = w_match.get("start")
                end = w_match.get("end")
                if "probability" in w_match:
                    conf = float(w_match["probability"])

            # Acoustic heuristic for challenging phonemes & syllable count
            # e.g., consonant clusters or ending sounds
            syllable_count = len(info["syllables"])
            if syllable_count >= 4 and conf > 0.85:
                conf -= 0.05
            if clean_word.endswith("ed") and syllable_count > 1 and conf > 0.82:
                conf -= 0.04

            conf = max(0.40, min(0.99, round(conf, 2)))
            total_confidence += conf

            # Words requiring attention (threshold 0.80)
            needs_review = conf < 0.80

            wp = WordPronunciation(
                word=word,
                expected_ipa=info["expected_ipa"],
                confidence=conf,
                start=start,
                end=end,
                needs_review=needs_review,
                syllables=info["syllables"],
                stress_index=info["stress_index"],
                feedback=info["feedback"] if needs_review else None
            )

            word_results.append(wp)
            if needs_review:
                problem_words.append(wp)

        # Rhythm & Pauses computation
        pause_count = 0
        total_pause_ms = 0.0
        speaking_ms = duration_ms

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

        pause_ratio = round(total_pause_ms / max(duration_ms, 1.0), 2)
        duration_s = max(duration_ms / 1000.0, 1.0)
        wpm = round((len(raw_words) / (duration_s / 60.0)), 1) if duration_s > 0 else 110.0

        # Rhythm consistency: optimal is around 110-140 WPM with < 25% pause ratio
        rhythm_score = 0.85
        if 100 <= wpm <= 150:
            rhythm_score += 0.10
        elif wpm < 80 or wpm > 180:
            rhythm_score -= 0.15

        if pause_ratio > 0.35:
            rhythm_score -= 0.10
        rhythm_score = max(0.40, min(1.0, round(rhythm_score, 2)))

        rhythm_metrics = RhythmMetrics(
            speech_rate_wpm=wpm,
            pause_count=pause_count,
            pause_duration_ratio=pause_ratio,
            rhythm_consistency_score=rhythm_score
        )

        # Overall pronunciation score (0 - 100)
        avg_word_conf = (total_confidence / len(raw_words)) if raw_words else 0.80
        overall_score = round((avg_word_conf * 0.70 + rhythm_score * 0.30) * 100, 1)

        # Band conversion according to IELTS descriptors
        if overall_score >= 88:
            band = 8.5
        elif overall_score >= 80:
            band = 7.5
        elif overall_score >= 72:
            band = 6.5
        elif overall_score >= 62:
            band = 5.5
        else:
            band = 4.5

        # Summary feedback
        if len(problem_words) == 0:
            summary = "Clear, intelligible pronunciation across all syllables with natural rhythm and flow."
        else:
            focus_words = ", ".join([f"'{p.word}' ({p.expected_ipa})" for p in problem_words[:3]])
            summary = f"Good overall intelligibility. Focus on distinct articulation and syllable stress for {focus_words}."

        return PronunciationReportResponse(
            overall_score=overall_score,
            estimated_band=band,
            word_count=len(raw_words),
            words=word_results,
            problem_words=problem_words,
            rhythm=rhythm_metrics,
            feedback_summary=summary
        )

    def evaluate_drill(
        self,
        target_word: str,
        user_spoken_text: Optional[str] = None,
        audio_confidence: Optional[float] = None
    ) -> PronunciationDrillResponse:
        clean_target = target_word.strip().lower()
        info = get_phonetic_info(clean_target)

        # Score calculation
        score = 85.0
        if audio_confidence is not None:
            score = round(audio_confidence * 100, 1)
        elif user_spoken_text:
            clean_spoken = user_spoken_text.strip().lower()
            if clean_spoken == clean_target:
                score = 92.0
            elif clean_target in clean_spoken:
                score = 84.0
            else:
                score = 62.0

        if score >= 90:
            accuracy = "Excellent"
        elif score >= 75:
            accuracy = "Good"
        else:
            accuracy = "Needs Practice"

        tips = [
            f"Expected IPA: {info['expected_ipa']}",
            f"Syllable breakdown: {' - '.join(info['syllables'])} (Stress: {info['syllables'][info['stress_index']].upper() if info['stress_index'] < len(info['syllables']) else ''})",
            info["feedback"]
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
            score=score,
            accuracy=accuracy,
            tips=tips,
            sample_sentence=sample_sentence
        )

_pronunciation_service = None

def get_pronunciation_service() -> PronunciationService:
    global _pronunciation_service
    if _pronunciation_service is None:
        _pronunciation_service = PronunciationService()
    return _pronunciation_service
