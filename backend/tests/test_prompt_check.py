"""Unit tests for the tutor's correction protocol (no local model required)."""

from app.prompts.tutor import build_conversation_messages, parse_corrections


def test_parse_corrections_and_say_it_again_prompt():
    response = (
        "Nice answer. What happened next?\n"
        '[CORRECTIONS]{"corrections":[{"original":"She don\'t",'
        '"corrected":"She doesn\'t","explanation":"Use does with she.",'
        '"category":"grammar","should_repeat":true}],'
        '"upgraded_sentence":"She doesn\'t drink coffee at all."}[/CORRECTIONS]'
    )

    clean_reply, corrections, repeat_prompt, upgraded_sentence = parse_corrections(response)

    assert clean_reply == "Nice answer. What happened next?"
    assert corrections == [{
        "original": "She don't",
        "corrected": "She doesn't",
        "explanation": "Use does with she.",
        "category": "grammar",
        "error_type": "grammar",
        "subtype": "general",
        "severity": "important",
        "practice_prompt": "Say a new sentence using: She doesn't",
        "should_repeat": True,
    }]
    assert repeat_prompt == 'Try saying: "She doesn\'t"'
    assert upgraded_sentence == "She doesn't drink coffee at all."


def test_conversation_prompt_contains_selected_correction_level():
    messages = build_conversation_messages(
        mode="daily", turns=[], topic="Travel", correction_level="none"
    )

    assert messages[0]["role"] == "system"
    assert "Correction Level: NONE" in messages[0]["content"]
    assert "Today's topic: Travel" in messages[0]["content"]
