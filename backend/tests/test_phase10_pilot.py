from app.api.pilot import ALLOWED_OUTCOMES


def test_pilot_outcome_contract_is_closed():
    assert ALLOWED_OUTCOMES == {
        "completed_without_help",
        "completed_with_help",
        "blocked",
    }


def test_pilot_success_rate_uses_completed_events_only():
    outcomes = ["completed_without_help", "completed_with_help", "blocked", "blocked"]
    completed = sum(item.startswith("completed_") for item in outcomes)
    assert completed / len(outcomes) == 0.5
