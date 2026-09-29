import httpx
import json
import time

def test_full_conversation_flow():
    client = httpx.Client(base_url="http://127.0.0.1:8000", timeout=60)

    print("=== 1. CREATING SESSION ===")
    s_res = client.post("/api/v1/sessions/", json={"mode": "daily", "topic": "Food and Cooking"})
    assert s_res.status_code == 200
    session = s_res.json()
    session_id = session["id"]
    print(f"Session ID: {session_id}")
    print(f"Mode: {session['mode']}, Topic: {session['topic']}")

    print("\n=== 2. TURN 1: User Speaks (with intentional grammatical errors) ===")
    user_text_1 = "Yesterday I go to the local market and buyed many fresh apples."
    print(f'User: "{user_text_1}"')

    t0 = time.time()
    conv_1 = client.post("/api/v1/conversation/respond", json={
        "session_id": session_id,
        "user_text": user_text_1,
        "mode": "daily"
    })
    t_conv_1 = round(time.time() - t0, 2)

    assert conv_1.status_code == 200, f"Error: {conv_1.text}"
    res_1 = conv_1.json()
    print(f"AI Reply ({t_conv_1}s): {res_1['message']}")
    print(f"Corrections count: {len(res_1['corrections'])}")
    if res_1["corrections"]:
        print("Corrections:")
        for c in res_1["corrections"]:
            print(f"  - [{c['original']}] -> [{c['corrected']}] ({c['explanation']})")

    print("\n=== 3. TURN 2: User Follow-up ===")
    user_text_2 = "I decided to bake an apple pie for my mother, and it smelled wonderful."
    print(f'User: "{user_text_2}"')

    t0 = time.time()
    conv_2 = client.post("/api/v1/conversation/respond", json={
        "session_id": session_id,
        "user_text": user_text_2,
        "mode": "daily"
    })
    t_conv_2 = round(time.time() - t0, 2)

    assert conv_2.status_code == 200, f"Error: {conv_2.text}"
    res_2 = conv_2.json()
    print(f"AI Reply ({t_conv_2}s): {res_2['message']}")
    print(f"Corrections count: {len(res_2['corrections'])}")

    print("\n=== 4. VERIFYING SESSION HISTORY & PERSISTENCE ===")
    hist_res = client.get(f"/api/v1/sessions/{session_id}")
    assert hist_res.status_code == 200
    history = hist_res.json()
    turns = history["turns"]
    print(f"Total Turns in Database: {len(turns)}")
    for i, turn in enumerate(turns, 1):
        print(f"  Turn {i} [{turn['role']}]: {turn['transcript']}")

    print("\n=== 5. FINISHING SESSION ===")
    fin_res = client.post(f"/api/v1/sessions/{session_id}/finish")
    assert fin_res.status_code == 200
    fin_data = fin_res.json()
    print(f"Session Status: Finished at {fin_data['ended_at']}")

    print("\n>>> ALL CHECKS PASSED SUCCESSFULLY! <<<")

if __name__ == "__main__":
    test_full_conversation_flow()
