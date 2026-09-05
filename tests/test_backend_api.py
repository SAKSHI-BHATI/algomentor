"""
test_backend_api.py — Integration tests for FastAPI endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from Backend.server import app

client = TestClient(app)


def test_home_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


def test_understanding_api():
    response = client.post("/api/understanding", json={
        "text": "I will store seen numbers in a hashmap",
        "problem_id": "two_sum",
        "problem_description": "Return indices of two numbers adding to target."
    })
    assert response.status_code == 200
    data = response.json()
    assert data.get("success") is True
    assert "result" in data


def test_hint_api():
    response = client.post("/api/hint", json={
        "problem_id": "two_sum",
        "code": "for i in range(n):",
        "thinking_state": "surface_thinking",
        "problem_description": "Two Sum"
    })
    assert response.status_code == 200
    data = response.json()
    assert data.get("success") is True
    assert "hints" in data
    assert isinstance(data["hints"], list)


def test_next_step_api():
    response = client.post("/api/next-step", json={
        "problem_id": "two_sum",
        "thought": "I will try all pairs",
        "thinking_state": "surface_thinking",
        "problem_description": "Two Sum"
    })
    assert response.status_code == 200
    data = response.json()
    assert data.get("success") is True
    assert "next_steps" in data


def test_evaluate_api():
    response = client.post("/api/evaluate", json={
        "code": "for i in range(n): for j in range(n): if arr[i] == arr[j]: return True"
    })
    assert response.status_code == 200
    data = response.json()
    assert data.get("success") is True
    assert "result" in data


def test_simulate_api():
    response = client.post("/api/simulate", json={
        "problem_id": "two_sum",
        "code": "",
        "input_data": {"nums": [2, 7, 11, 15], "target": 9},
        "use_optimal": False
    })
    assert response.status_code == 200
    data = response.json()
    assert data.get("success") is True
    assert "steps" in data
