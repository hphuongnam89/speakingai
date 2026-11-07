"""Transcript-only assessment boundaries. No held-out calibration has been validated."""
VERSION = "assessment-0.4"
PROMPT_VERSION = "ielts-transcript-0.4"
MIN_WORDS = 40  # Sufficiency policy for this preview; not an IELTS or calibration threshold.


def band(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value) if 1 <= value <= 9 and value * 2 == int(value * 2) else None


def abstain(reason="Model output could not be verified"):
    return {"overall_band": None, "fluency_score": None, "lexical_score": None, "grammar_score": None,
            "pronunciation_score": None, "fluency_feedback": "", "lexical_feedback": "", "grammar_feedback": "",
            "strengths": [], "areas_for_improvement": [], "suggested_expressions": [],
            "examiner_summary": reason, "score_status": "unavailable", "confidence": None,
            "confidence_range": "Unverified; no validated uncertainty interval",
            "limitation": "Pronunciation and temporal fluency are not scored from transcript alone. Overall band is unavailable.",
            "scoring_version": VERSION, "model_id": None, "provider": None, "prompt_version": PROMPT_VERSION}


def parse_payload(data):
    result = abstain()
    if not isinstance(data, dict):
        return result
    scores = {k: band(data.get(k)) for k in ("fluency_score", "lexical_score", "grammar_score")}
    if any(scores[k] is None for k in ("lexical_score", "grammar_score")):
        return result
    for key in ("fluency_feedback", "lexical_feedback", "grammar_feedback", "examiner_summary"):
        value = data.get(key, "")
        if not isinstance(value, str) or len(value) > 6000:
            return abstain()
        result[key] = value
    for key in ("strengths", "areas_for_improvement"):
        value = data.get(key, [])
        if not isinstance(value, list) or len(value) > 20 or any(not isinstance(v, str) or len(v) > 2000 for v in value):
            return abstain()
        result[key] = value
    expressions = data.get("suggested_expressions", [])
    if not isinstance(expressions, list) or len(expressions) > 20:
        return abstain()
    for item in expressions:
        if not isinstance(item, dict) or any(not isinstance(item.get(k), str) or len(item[k]) > 2000 for k in ("original", "upgraded")):
            return abstain()
        if item.get("context") is not None and (not isinstance(item["context"], str) or len(item["context"]) > 2000):
            return abstain()
    result.update(scores, suggested_expressions=[{k: item[k] for k in ("original", "upgraded", "context") if k in item}
                                                for item in expressions], score_status="provisional")
    return result


def report(payload, turns, metadata=None):
    result = dict(payload)
    words = sum(len(t.transcript.split()) for t in turns if t.role == "user")
    if words < MIN_WORDS:
        result = abstain(f"Insufficient evidence: at least {MIN_WORDS} learner words are required by the preview policy.")
        result["score_status"] = "insufficient_evidence"
    elif result.get("score_status") == "provisional" and not all((metadata or {}).get(k) for k in ("provider_used", "model_used")):
        result = abstain("Assessment provenance is unavailable; no numeric estimate is shown.")
    # The model only receives text, even if a recording exists elsewhere in the session.
    result.update(overall_band=None, fluency_score=None, pronunciation_score=None, confidence=None,
                  confidence_range="Unverified; no validated uncertainty interval", scoring_version=VERSION,
                  prompt_version=PROMPT_VERSION, evidence_words=words)
    result["fluency_feedback"] = "Temporal fluency requires an audio-aware assessment; transcript-only scoring abstains."
    result["limitation"] = abstain()["limitation"]
    result["provider"] = (metadata or {}).get("provider_used")
    result["model_id"] = (metadata or {}).get("model_used")
    return result
