import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from starlette.testclient import TestClient
from app.main import app
from app.core.database import init_db

def test_phase2_ai_tutor():
    init_db()
    client = TestClient(app)

    print("=== 1. TESTING USER SETTINGS ===")
    res_get_settings = client.get("/api/v1/settings")
    assert res_get_settings.status_code == 200, res_get_settings.text
    initial_settings = res_get_settings.json()
    print("Initial Settings:", initial_settings)

    res_put_settings = client.put("/api/v1/settings", json={"correction_level": "aggressive"})
    assert res_put_settings.status_code == 200, res_put_settings.text
    updated_settings = res_put_settings.json()
    assert updated_settings["correction_level"] == "aggressive"
    print("Updated Settings:", updated_settings["correction_level"])

    print("\n=== 2. CREATING SESSION & CONVERSATION WITH ERROR ===")
    s_res = client.post("/api/v1/sessions/", json={"mode": "daily", "topic": "Weekend Activities"})
    assert s_res.status_code == 200
    session_id = s_res.json()["id"]

    # User says something with an error: "She don't like playing tennis"
    conv_1 = client.post("/api/v1/conversation/respond", json={
        "session_id": session_id,
        "user_text": "She don't like playing tennis with us on Sunday.",
        "mode": "daily",
        "correction_level": "important"
    })
    assert conv_1.status_code == 200, conv_1.text
    res_1 = conv_1.json()
    print(f"AI Reply: {res_1['message'][:120]}...")
    print(f"Repeat prompt (Say-it-again): {res_1['repeat_prompt']}")
    print(f"Corrections: {res_1['corrections']}")

    print("\n=== 3. VERIFYING MISTAKE WAS STORED IN DATABASE ===")
    m_res = client.get("/api/v1/mistakes")
    assert m_res.status_code == 200, m_res.text
    mistakes = m_res.json()
    print(f"Total stored mistakes: {len(mistakes)}")
    assert len(mistakes) > 0, "Expected at least 1 mistake stored"
    target_mistake = mistakes[0]
    print(f"Stored mistake: '{target_mistake['original_text']}' -> '{target_mistake['corrected_text']}', Occurrences: {target_mistake['occurrence_count']}")

    print("\n=== 4. REPEATING THE SAME ERROR IN TURN 2 (OCCURRENCE INCREMENT) ===")
    conv_2 = client.post("/api/v1/conversation/respond", json={
        "session_id": session_id,
        "user_text": "Also my brother don't like tennis too.",
        "mode": "daily",
        "correction_level": "important"
    })
    assert conv_2.status_code == 200, conv_2.text

    # Let's test direct repository duplicate test or check frequent mistakes
    freq_res = client.get("/api/v1/mistakes/frequent")
    assert freq_res.status_code == 200
    frequent = freq_res.json()
    print(f"Frequent mistakes count: {len(frequent)}")
    for f in frequent:
        print(f"  - '{f['original_text']}': repeated {f['occurrence_count']} time(s), resolved={f['resolved']}")

    print("\n=== 5. RESOLVING A MISTAKE ===")
    mistake_id = target_mistake["id"]
    res_resolve = client.post(f"/api/v1/mistakes/{mistake_id}/resolve")
    assert res_resolve.status_code == 200
    assert res_resolve.json()["resolved"] is True
    print(f"Mistake {mistake_id} marked as resolved: True")

    print("\n=== 6. TESTING CORRECTION LEVEL = 'NONE' ===")
    s_res_none = client.post("/api/v1/sessions/", json={"mode": "freetalk", "topic": "Movies"})
    session_id_none = s_res_none.json()["id"]

    conv_none = client.post("/api/v1/conversation/respond", json={
        "session_id": session_id_none,
        "user_text": "Yesterday I go see Batman movie with my friends.",
        "mode": "freetalk",
        "correction_level": "none"
    })
    assert conv_none.status_code == 200
    res_none = conv_none.json()
    print(f"Correction level NONE result: corrections count = {len(res_none['corrections'])}, message = {res_none['message'][:100]}...")
    assert len(res_none['corrections']) == 0, "Expected zero corrections when level is 'none'"

    print("\n>>> ALL PHASE 2 AI TUTOR TESTS PASSED SUCCESSFULLY! <<<")

if __name__ == "__main__":
    test_phase2_ai_tutor()
