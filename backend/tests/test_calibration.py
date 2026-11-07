import json
from types import SimpleNamespace

from app.services.scoring_calibration import apply_calibration


def test_calibration_requires_consent_and_minimum_samples():
    samples = [SimpleNamespace(consented="true", human_fc=7.0, human_lr=7.0, human_gra=7.0, human_pronunciation=6.5, ai_payload_json=json.dumps({"fluency_score": 6.0, "lexical_score": 6.0, "grammar_score": 6.0, "pronunciation_score": 6.0})) for _ in range(5)]
    result = apply_calibration({"overall_band": 6.0, "fluency_score": 6.0, "lexical_score": 6.0, "grammar_score": 6.0, "pronunciation_score": 6.0}, samples)
    assert result.get("score_status") != "calibrated"
    assert result["overall_band"] == 6.0
    assert result["fluency_score"] == 6.0
    assert result["confidence"] is None


def test_calibration_stays_provisional_without_consent():
    sample = SimpleNamespace(consented="false", human_fc=8.0, human_lr=8.0, human_gra=8.0, human_pronunciation=8.0, ai_payload_json=json.dumps({"fluency_score": 6.0, "lexical_score": 6.0, "grammar_score": 6.0, "pronunciation_score": 6.0}))
    result = apply_calibration({"overall_band": 6.0, "fluency_score": 6.0, "lexical_score": 6.0, "grammar_score": 6.0}, [sample])
    assert result.get("score_status") != "calibrated"
