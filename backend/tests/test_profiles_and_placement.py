from fastapi.testclient import TestClient
from app.main import app
from app.core.database import init_db

init_db()
client = TestClient(app)


def test_list_and_create_profile():
    # Listing profiles on fresh install
    res = client.get("/api/v1/profiles")
    assert res.status_code == 200
    profiles = res.json()
    assert isinstance(profiles, list)

    # Create a new profile
    new_profile_data = {
        "name": "Nam Test",
        "target_band": 7.5,
        "daily_target_minutes": 30,
        "target_duration_months": 3,
        "avatar_color": "#059669"
    }
    create_res = client.post("/api/v1/profiles", json=new_profile_data)
    assert create_res.status_code == 200
    created = create_res.json()
    assert created["name"] == "Nam Test"
    assert created["target_band"] == 7.5
    assert created["daily_target_minutes"] == 30
    assert created["placement_status"] == "not_started"
    assert created["is_active"] is True

    # List again, should have at least 1
    res2 = client.get("/api/v1/profiles")
    assert len(res2.json()) >= 1


def test_placement_questions():
    res = client.get("/api/v1/placement/questions")
    assert res.status_code == 200
    data = res.json()
    assert "questions" in data
    assert len(data["questions"]) == 3
    assert data["questions"][0]["level"] == "A2-B1"
    assert data["questions"][1]["level"] == "B1-B2"
    assert data["questions"][2]["level"] == "B2-C1"


def test_edit_profile_and_recalculate_roadmap():
    # Create profile
    p_data = {
        "name": "Edit Learner",
        "target_band": 7.0,
        "daily_target_minutes": 20,
        "target_duration_months": 3
    }
    create_res = client.post("/api/v1/profiles", json=p_data)
    assert create_res.status_code == 200
    pid = create_res.json()["id"]

    # Update profile (edit target band and minutes)
    update_data = {
        "name": "Edit Learner Updated",
        "target_band": 8.0,
        "daily_target_minutes": 60,
        "target_duration_months": 5
    }
    up_res = client.put(f"/api/v1/profiles/{pid}", json=update_data)
    assert up_res.status_code == 200
    updated = up_res.json()
    assert updated["name"] == "Edit Learner Updated"
    assert updated["target_band"] == 8.0
    assert updated["daily_target_minutes"] == 60
    assert updated["target_duration_months"] == 5

    # Recalculate roadmap
    recalc_res = client.post(f"/api/v1/profiles/{pid}/roadmap/recalculate")
    assert recalc_res.status_code == 200
    recalculated = recalc_res.json()
    assert recalculated["roadmap_data"] is not None
    rm = recalculated["roadmap_data"]["roadmap"]
    assert rm["total_hours"] == 150.0  # 60 min * 5 months * 30 days / 60 min = 150 hours
    assert len(rm["phases"]) == 3

    # Reset placement test
    reset_res = client.post(f"/api/v1/profiles/{pid}/placement/reset")
    assert reset_res.status_code == 200
    assert reset_res.json()["placement_status"] == "not_started"
    assert reset_res.json()["current_band"] is None
