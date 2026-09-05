"""
test_auth_and_db.py — Integration test suite for AlgoMentor authentication, DB, and AI service
"""

import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from Backend.server import app
from Backend.database import init_db, SessionLocal
from Backend.data_seeder import seed_database
from AI_engine.services.ai_service import ai_service

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_test_database():
    seed_database()


def test_database_problem_seeding():
    response = client.get("/api/problems")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["problems"]) >= 10


def test_get_single_problem_details():
    response = client.get("/api/problems/two-sum")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["problem"]["title"] == "Two Sum"
    assert len(data["problem"]["constraints"]) > 0


def test_user_registration_and_login():
    # Keep the test independent of prior local runs; the application rightly
    # rejects duplicate registrations in its persistent SQLite database.
    email = f"teststudent_{uuid4().hex}@algomentor.com"
    password = "securepassword123"

    # 1. Register
    reg_res = client.post("/api/auth/register", json={
        "email": email,
        "password": password,
        "name": "Test Student"
    })
    assert reg_res.status_code == 200
    reg_data = reg_res.json()
    assert reg_data["success"] is True
    assert "token" in reg_data

    # 2. Login
    login_res = client.post("/api/auth/login", json={
        "email": email,
        "password": password
    })
    assert login_res.status_code == 200
    token = login_res.json()["token"]

    # 3. Verify /me with Bearer token
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["user"]["email"] == email


def test_progress_saving_and_retrieval():
    # Login as demo user
    login_res = client.post("/api/auth/login", json={
        "email": "demo@algomentor.com",
        "password": "demo123"
    })
    token = login_res.json()["token"]

    # Save progress
    save_res = client.post("/api/progress/save", json={
        "problem_id": "two-sum",
        "status": "solved",
        "whiteboard_content": "def two_sum(nums, target): return [0, 1]",
        "flowchart_data": [{"id": 1, "label": "Start"}],
        "concept_breakdown": {"input": "nums, target"}
    }, headers={"Authorization": f"Bearer {token}"})
    assert save_res.status_code == 200
    assert save_res.json()["success"] is True

    # Retrieve progress
    prog_res = client.get("/api/progress/two-sum", headers={"Authorization": f"Bearer {token}"})
    assert prog_res.status_code == 200
    prog_data = prog_res.json()["progress"]
    assert prog_data["status"] == "solved"
    assert "two_sum" in prog_data["whiteboard_content"]


def test_ai_service_5_level_hints():
    hints = ai_service.get_progressive_hints(
        problem_id="two-sum",
        code="def two_sum(): pass",
        thinking_state="surface_thinking",
        problem_description="Find two numbers"
    )
    assert len(hints) == 5
    assert hints[0]["level"] == 1
    assert hints[4]["level"] == 5


def test_ai_service_pseudocode_evaluation():
    eval_res = ai_service.evaluate_pseudocode("seen = {}; for i, num in enumerate(nums): if target - num in seen: return [seen[target-num], i]; seen[num] = i")
    assert eval_res["status"] == "success"
    assert eval_res["label"] in ["optimal", "better", "brute_force"]
    assert "time_complexity" in eval_res
