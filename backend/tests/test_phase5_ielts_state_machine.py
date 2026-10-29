from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_part2_timing_warning_when_too_short():
    start_resp = client.post("/api/v1/ielts/start", json={"part": "part2"})
    assert start_resp.status_code == 200
    session_id = start_resp.json()["session_id"]
    assert start_resp.json()["cue_card"] is not None

    # Candidate speaks a very short answer (< 75 words)
    short_speech = "I want to talk about my journey to Da Nang last year. It was nice."
    resp = client.post("/api/v1/ielts/respond", json={
        "session_id": session_id,
        "user_text": short_speech,
        "part": "part2"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_completed"] is True
    assert data["timing_warning"] is not None
    assert "dưới 1 phút" in data["timing_warning"]


def test_full_mock_evaluation_rejected_when_incomplete():
    # Start Full Mock
    start_resp = client.post("/api/v1/ielts/start", json={"part": "full_mock"})
    assert start_resp.status_code == 200
    session_id = start_resp.json()["session_id"]

    # Candidate only answers 1 question in Part 1
    client.post("/api/v1/ielts/respond", json={
        "session_id": session_id,
        "user_text": "I am currently a full-time university student majoring in information technology.",
        "part": "part1"
    })

    # Try to trigger evaluation prematurely
    eval_resp = client.post(f"/api/v1/ielts/evaluate/{session_id}")
    assert eval_resp.status_code == 400
    detail = eval_resp.json()["detail"]
    assert detail["error_code"] == "FULL_MOCK_INCOMPLETE"


def test_full_mock_state_machine_progresses_through_all_parts():
    # 1. Start Full Mock
    start_resp = client.post("/api/v1/ielts/start", json={"part": "full_mock"})
    assert start_resp.status_code == 200
    session_id = start_resp.json()["session_id"]
    assert "ielts" in start_resp.json()["greeting"].lower() or "examiner" in start_resp.json()["greeting"].lower()

    # 2. Complete Part 1 (4 turns)
    for i in range(4):
        p1_resp = client.post("/api/v1/ielts/respond", json={
            "session_id": session_id,
            "user_text": f"This is my detailed Part 1 response for question {i+1} sharing my experience.",
            "part": "part1"
        })
        assert p1_resp.status_code == 200
        p1_data = p1_resp.json()
        if i < 3:
            assert p1_data["is_completed"] is False
            assert p1_data["next_part"] == "part1"
        else:
            # 4th answer must transition to Part 2 with a Cue Card!
            assert p1_data["is_completed"] is False
            assert p1_data["next_part"] == "part2"
            assert p1_data["cue_card"] is not None
            assert len(p1_data["cue_card"]["bullets"]) >= 3

    # 3. Submit Part 2 long turn
    part2_speech = (
        "I would like to describe a memorable trip I had with my family to the mountains. "
        "We prepared our backpacks with warm clothes and local snacks. During the trip, we went hiking, "
        "visited an ancient temple, and enjoyed breathtaking panoramic views of the entire valley. "
        "This journey was unforgettable because it gave us precious time to connect deeply after months of busy work."
    )
    p2_resp = client.post("/api/v1/ielts/respond", json={
        "session_id": session_id,
        "user_text": part2_speech,
        "part": "part2"
    })
    assert p2_resp.status_code == 200
    p2_data = p2_resp.json()
    # Must transition to Part 3
    assert p2_data["is_completed"] is False
    assert p2_data["next_part"] == "part3"
    assert "part 3" in p2_data["message"].lower()

    # 4. Complete Part 3 (3 turns)
    for j in range(3):
        p3_resp = client.post("/api/v1/ielts/respond", json={
            "session_id": session_id,
            "user_text": f"From my perspective, societal development brings both opportunities and challenges {j+1}.",
            "part": "part3"
        })
        assert p3_resp.status_code == 200
        p3_data = p3_resp.json()
        if j < 2:
            assert p3_data["is_completed"] is False
            assert p3_data["next_part"] == "part3"
        else:
            # Final turn completes Full Mock!
            assert p3_data["is_completed"] is True
            assert p3_data["next_part"] == "completed"
            assert "end of the speaking test" in p3_data["message"].lower()
