import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from starlette.testclient import TestClient
from app.main import app
from app.core.database import init_db

client = TestClient(app)

def test_phase5_pronunciation_engine():
    init_db()

    print("\n=== 1. TEST PHONETIC DICTIONARY LOOKUP ===")
    res_dict = client.get("/api/v1/pronunciation/dictionary/enjoyed")
    assert res_dict.status_code == 200, res_dict.text
    data_dict = res_dict.json()
    print("Enjoyed info:", data_dict)
    assert data_dict["word"] == "enjoyed"
    assert "/ɪnˈdʒɔɪd/" in data_dict["expected_ipa"]
    assert "enjoyed" in data_dict["syllables"] or "joyed" in data_dict["syllables"]

    res_dict2 = client.get("/api/v1/pronunciation/dictionary/technology")
    assert res_dict2.status_code == 200
    assert "tɛkˈnɒlədʒi" in res_dict2.json()["expected_ipa"]

    print("\n=== 2. TEST PRONUNCIATION ANALYSIS ENDPOINT ===")
    sample_text = "I really enjoyed learning modern technology and environmental science."
    res_analysis = client.post("/api/v1/pronunciation/analyze", json={
        "text": sample_text,
        "audio_duration_ms": 4200
    })
    assert res_analysis.status_code == 200, res_analysis.text
    report = res_analysis.json()
    print(f"Recognition confidence: {report['recognition_confidence']}")
    print(f"Experimental pronunciation score: {report['pronunciation_score']}")
    print(f"Total Words Analyzed: {report['word_count']}")
    print(f"Words: {len(report['words'])}")
    print(f"Rhythm (WPM): {report['rhythm']['speech_rate_wpm']}")
    print(f"Feedback: {report['feedback_summary']}")

    assert report["word_count"] > 0
    assert len(report["words"]) == report["word_count"]
    assert report["recognition_confidence"] is None
    assert report["pronunciation_score"] is None
    assert "not an IELTS result" in report["disclaimer"]
    for w in report["words"]:
        assert "expected_ipa" in w
        assert "confidence" in w
        assert w["confidence"] is None

    print("\n=== 3. TEST PRONUNCIATION DRILL (LISTEN, RECORD, REPEAT) ===")
    res_drill = client.post("/api/v1/pronunciation/drill", json={
        "target_word": "technology"
    })
    assert res_drill.status_code == 200, res_drill.text
    drill_data = res_drill.json()
    print(f"Drill score for '{drill_data['word']}': {drill_data['score']} ({drill_data['accuracy']})")
    print(f"Tips: {drill_data['tips']}")
    print(f"Sample Sentence: {drill_data['sample_sentence']}")
    assert drill_data["score"] is None
    assert drill_data["accuracy"] == "Not scored"

    print("\n=== 4. TEST INTEGRATION IN CONVERSATION TURN ===")
    # Create session
    s_res = client.post("/api/v1/sessions/", json={"mode": "daily", "topic": "Weekend"})
    assert s_res.status_code == 200
    session_id = s_res.json()["id"]

    # Send conversation turn
    conv_res = client.post("/api/v1/conversation/respond", json={
        "session_id": session_id,
        "user_text": "I enjoyed the delicious cuisine and relaxing weather.",
        "mode": "daily"
    })
    assert conv_res.status_code == 200, conv_res.text
    conv_data = conv_res.json()
    assert "pronunciation" in conv_data
    pron = conv_data["pronunciation"]
    assert pron is None

    print("\n>>> ALL PHASE 5 PRONUNCIATION ENGINE BACKEND TESTS PASSED! <<<")

if __name__ == "__main__":
    test_phase5_pronunciation_engine()
