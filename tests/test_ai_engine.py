"""
test_ai_engine.py — Unit tests for AlgoMentor AI Engine models and pipeline.
"""

import pytest
from AI_engine.pipeline.orchestrator import run_pipeline
from AI_engine.model_logic.understanding_model import predict as predict_understanding
from AI_engine.model_logic.hint_generation_model import predict as predict_hint
from AI_engine.model_logic.reasoning_next_step_model import predict as predict_next_step
from AI_engine.model_logic.pseudocode_evaluation_model import predict as predict_pseudo
from AI_engine.model_logic.bridge_model import generate_bridge_options
from AI_engine.services.mentor_service import mentor_service
from AI_engine.services.ai_service import ai_service


def test_understanding_model():
    res = predict_understanding(
        text="I will use a hashmap to store complement values",
        problem_id="two_sum",
        problem_description="Find two numbers that sum to target."
    )
    assert "thinking_state" in res
    assert "prediction" in res
    assert res["prediction"] in ["PROCEED", "WATCH"]
    assert isinstance(res["confidence"], float)


def test_hint_model():
    hints = predict_hint(
        problem_id="two_sum",
        code="for i in range(n): for j in range(n):",
        thinking_state="surface_thinking",
        problem_description="Two Sum problem"
    )
    assert isinstance(hints, list)
    assert len(hints) > 0
    assert isinstance(hints[0], str)


def test_next_step_model():
    steps = predict_next_step(
        user_input="I will check every pair using nested loops",
        problem_id="two_sum",
        thinking_state="surface_thinking",
        problem_description="Two Sum problem"
    )
    assert isinstance(steps, list)
    assert len(steps) == 3


def test_bridge_model_3_options_confidence():
    options = generate_bridge_options(
        user_thought="I am stuck on how to find pairs",
        problem_id="two-sum",
        problem_title="Two Sum"
    )
    assert isinstance(options, list)
    assert len(options) == 3

    confidences = [opt["confidence"] for opt in options]
    assert "solid" in confidences
    assert "exploratory" in confidences
    assert "risky" in confidences

    # Enforce design constraint: not all 3 options lead to solution!
    solutions = [opt["leads_to_solution"] for opt in options]
    assert False in solutions  # Must contain at least one non-solution option


def test_mentor_service_understand_and_review():
    u_res = mentor_service.understand_problem("two-sum", "Two Sum", "Find two numbers")
    assert u_res["status"] == "success"
    assert "simplified_explanation" in u_res
    assert "real_world_analogy" in u_res

    p_res = mentor_service.pattern_hint("two-sum", "Two Sum")
    assert p_res["status"] == "success"
    assert "socratic_question" in p_res

    r_res = mentor_service.review_code("two-sum", "def two_sum(nums, target): return []")
    assert r_res["status"] == "success"
    assert r_res["rewrite_provided"] is False  # Explains without rewriting code!


def test_ai_service_bridge_and_mentor_pipeline():
    opts = ai_service.get_bridge_options(thought="How to optimize search?", problem_id="two-sum")
    assert len(opts) == 3

    m_rev = ai_service.review_code("two-sum", "def two_sum(nums, target): pass")
    assert m_rev["status"] == "success"
