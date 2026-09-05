"""Regression coverage for frontend/backend problem-ID compatibility."""

from fastapi.testclient import TestClient

from Backend.data_seeder import seed_database
from Backend.server import app


client = TestClient(app)


def test_problem_and_progress_accept_snake_case_ids():
    seed_database()
    login = client.post("/api/auth/login", json={
        "email": "demo@algomentor.com", "password": "demo123"
    })
    token = login.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    detail = client.get("/api/problems/two_sum")
    assert detail.status_code == 200
    assert detail.json()["problem"]["id"] == "two-sum"

    saved = client.post("/api/progress/save", headers=headers, json={
        "problem_id": "two_sum", "status": "attempted"
    })
    assert saved.status_code == 200
    assert saved.json()["success"] is True

    progress = client.get("/api/progress/two-sum", headers=headers)
    assert progress.status_code == 200
    assert progress.json()["progress"] is not None
