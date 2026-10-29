import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from starlette.testclient import TestClient
from app.main import app

client = TestClient(app)





def test_ielts_part1_flow():
    print("\n=== TEST 1: IELTS PART 1 START ===")
    res = client.post("/api/v1/ielts/start", json={"part": "part1"})
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["part"] == "part1"
    assert "session_id" in data
    assert len(data["question"]) > 0
    print(f"Session ID: {data['session_id']}")
    print(f"Examiner Greeting: {data['greeting']}")
    print(f"First Question: {data['question']}")

    session_id = data["session_id"]

    # Candidate answers
    print("\n=== TEST 2: IELTS CANDIDATE RESPONDS ===")
    ans_res = client.post("/api/v1/ielts/respond", json={
        "session_id": session_id,
        "user_text": "I am currently working as a software developer in a technology firm. I enjoy solving complex logic puzzles.",
        "part": "part1"
    })
    assert ans_res.status_code == 200, ans_res.text
    ans_data = ans_res.json()
    print(f"Examiner follow-up: {ans_data['message']}")
    assert len(ans_data["message"]) > 0

def test_ielts_part2_cue_card():
    print("\n=== TEST 3: IELTS PART 2 CUE CARD ===")
    res = client.post("/api/v1/ielts/start", json={"part": "part2"})
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["part"] == "part2"
    assert data["cue_card"] is not None
    cue = data["cue_card"]
    print(f"Cue Card Topic: {cue['topic']}")
    print(f"Cue Card Title: {cue['title']}")
    print(f"Bullets: {cue['bullets']}")
    assert len(cue["bullets"]) == 4

    session_id = data["session_id"]
    # Candidate speaks their 2-minute long turn
    long_turn_text = (
        "I would like to describe a memorable trip I took to Da Nang two years ago with my close college friends. "
        "We traveled by airplane from Hanoi and spent four days exploring the coastal city. "
        "During our time there, we swam in My Khe beach, visited the Marble Mountains, and enjoyed authentic local cuisines like Mi Quang. "
        "This journey was unforgettable because it was our last travel together before starting our careers."
    )
    ans_res = client.post("/api/v1/ielts/respond", json={
        "session_id": session_id,
        "user_text": long_turn_text,
        "part": "part2"
    })
    assert ans_res.status_code == 200
    ans_data = ans_res.json()
    assert ans_data["is_completed"] is True
    print(f"Part 2 conclusion: {ans_data['message']}")

    # Evaluation
    print("\n=== TEST 4: IELTS EVALUATION RESPONSE CONTRACT ===")
    eval_res = client.post(f"/api/v1/ielts/evaluate/{session_id}")
    assert eval_res.status_code == 200, eval_res.text

    eval_data = eval_res.json()
    print(f"Overall Band: {eval_data['overall_band']}")
    print(f"Fluency & Coherence: {eval_data['fluency_score']} - {eval_data['fluency_feedback']}")
    print(f"Lexical Resource: {eval_data['lexical_score']} - {eval_data['lexical_feedback']}")
    print(f"Grammar: {eval_data['grammar_score']} - {eval_data['grammar_feedback']}")
    print(f"Strengths: {eval_data['strengths']}")
    print(f"Suggested Upgrades: {eval_data['suggested_expressions']}")
    print(f"Disclaimer: {eval_data['disclaimer']}")

    assert 1.0 <= eval_data["overall_band"] <= 9.0
    assert "Estimated score" in eval_data["disclaimer"]
    print("\n>>> ALL IELTS PHASE 3 BACKEND TESTS PASSED! <<<")

def test_ielts_topics_catalog():
    res = client.get("/api/v1/ielts/topics")
    assert res.status_code == 200
    data = res.json()
    assert "part1" in data and len(data["part1"]) >= 5
    assert "part2" in data and len(data["part2"]) >= 4
    assert "daily" in data and len(data["daily"]) >= 3

def test_ielts_specific_topic_selection():
    # Test starting Part 1 with a specific topic
    res_p1 = client.post("/api/v1/ielts/start", json={"part": "part1", "topic": "Food & Cooking"})
    assert res_p1.status_code == 200
    d1 = res_p1.json()
    assert "food" in d1["question"].lower() or "cooking" in d1["question"].lower()

    # Test starting Part 2 with a specific cue card topic
    res_p2 = client.post("/api/v1/ielts/start", json={"part": "part2", "topic": "An Inspiring Person"})
    assert res_p2.status_code == 200
    d2 = res_p2.json()
    assert d2["cue_card"]["topic"] == "An Inspiring Person"

if __name__ == "__main__":
    test_ielts_part1_flow()
    test_ielts_part2_cue_card()
