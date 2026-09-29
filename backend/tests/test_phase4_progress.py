import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from starlette.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal, init_db
from app.repositories.progress_repo import ProgressRepository

client = TestClient(app)

def test_progress_and_adaptive_learning():
    init_db()
    print("\n=== 1. RECORD ACTIVITY & CHECK SUMMARY ===")
    # Seed some sample activity for today
    with SessionLocal() as db:
        repo = ProgressRepository(db)
        repo.record_activity(
            user_id="default",
            speaking_minutes=5.0,
            words=520,
            mistakes=2,
            band=6.5
        )

    res_summary = client.get("/api/v1/progress/summary")
    assert res_summary.status_code == 200, res_summary.text
    summary = res_summary.json()
    print("Summary:", summary)
    assert summary["streak"] >= 1
    assert summary["total_speaking_minutes"] >= 5.0
    assert summary["total_sessions"] >= 1
    assert summary["avg_wpm"] > 0
    assert summary["latest_band"] is not None

    print("\n=== 2. CHECK WEEKLY PROGRESS VIEW ===")
    res_weekly = client.get("/api/v1/progress/weekly")
    assert res_weekly.status_code == 200, res_weekly.text
    weekly = res_weekly.json()
    print(f"Weekly stats count: {len(weekly)}")
    assert len(weekly) == 7
    for day in weekly:
        print(f"  - {day['day_of_week']} ({day['date']}): {day['speaking_minutes']} mins, {day['session_count']} sessions, {day['mistake_count']} mistakes")

    print("\n=== 3. ADAPTIVE LEARNING PLAN (OLLAMA GENERATED) ===")
    res_plan = client.get("/api/v1/progress/adaptive-plan")
    assert res_plan.status_code == 200, res_plan.text
    plan = res_plan.json()
    print("Today's Objective:", plan["today_objective"])
    print("Targeted Weaknesses:", plan["top_weaknesses"])
    print("Recommended Topic:", plan["recommended_topic"])
    print("Challenge Phrases:", plan["challenge_phrases"])

    assert len(plan["today_objective"]) > 0
    assert len(plan["top_weaknesses"]) > 0
    assert len(plan["recommended_topic"]) > 0

    print("\n>>> ALL PHASE 4 PROGRESS & ADAPTIVE LEARNING TESTS PASSED! <<<")

if __name__ == "__main__":
    test_progress_and_adaptive_learning()
