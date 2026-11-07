"""Calibration remains unverified until a separate held-out evaluation is approved."""
from app.services.assessment import abstain


def apply_calibration(payload: dict, samples: list[object], minimum_samples: int = 5) -> dict:
    # Sample count and in-sample bias fitting cannot establish out-of-sample accuracy.
    result = dict(payload)
    result.update(confidence=None, confidence_range=abstain()["confidence_range"])
    if result.get("score_status") == "calibrated":
        result["score_status"] = "provisional"
    result.pop("calibration_corrections", None)
    result["calibration_status"] = "unverified"
    return result
