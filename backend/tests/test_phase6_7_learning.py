from app.prompts.tutor import parse_corrections


def test_correction_parser_adds_learning_fields_on_json():
    text = '[CORRECTIONS]{"corrections":[{"original":"she go","corrected":"she goes","explanation":"third person singular","category":"grammar","subtype":"subject_verb_agreement","practice_prompt":"Say a new sentence with she goes.","should_repeat":true}]}[/CORRECTIONS]'
    _, corrections, repeat_prompt, _ = parse_corrections(text)
    assert corrections[0]["error_type"] == "grammar"
    assert corrections[0]["subtype"] == "subject_verb_agreement"
    assert corrections[0]["practice_prompt"]
    assert repeat_prompt


def test_correction_parser_limits_focus_errors():
    text = '[CORRECTIONS]{"corrections":[' + ','.join('{"original":"a","corrected":"b"}' for _ in range(5)) + ']}[/CORRECTIONS]'
    _, corrections, _, _ = parse_corrections(text)
    assert len(corrections) <= 3
