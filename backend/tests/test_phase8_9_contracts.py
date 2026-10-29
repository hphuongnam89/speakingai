from app.prompts.ielts import parse_evaluation


def test_evaluation_parser_is_provisional_without_pronunciation():
    result = parse_evaluation('[EVALUATION]{"overall_band":6.5,"fluency_score":6.5,"lexical_score":6.0,"grammar_score":6.0,"pronunciation_score":8.0}[/EVALUATION]')
    assert result["pronunciation_score"] is None
    assert result["score_status"] == "provisional"
    assert result["confidence_range"]
    assert "Pronunciation" in result["limitation"]


def test_malformed_evaluation_has_low_confidence_fallback():
    result = parse_evaluation("not json")
    assert result["confidence"] <= 0.5
    assert result["scoring_version"] == "phase8-v1"
