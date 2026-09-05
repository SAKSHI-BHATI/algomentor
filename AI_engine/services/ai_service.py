"""
ai_service.py — Hybrid AI Service Abstraction for AlgoMentor
"""

import os
import json
import numpy as np

# Local trained models & services
from AI_engine.model_logic.understanding_model import predict as predict_understanding_local
from AI_engine.model_logic.hint_generation_model import predict as predict_hints_local
from AI_engine.model_logic.reasoning_next_step_model import predict as predict_next_steps_local
from AI_engine.model_logic.pseudocode_evaluation_model import predict as predict_pseudo_local
from AI_engine.model_logic.bridge_model import generate_bridge_options
from AI_engine.services.mentor_service import mentor_service


class AIService:
    def __init__(self):
        self.provider = os.getenv("AI_PROVIDER", "local_hybrid").lower()
        self.model = os.getenv("AI_MODEL", "claude-3-5-sonnet-20241022")
        self.api_key = os.getenv("AI_API_KEY", os.getenv("ANTHROPIC_API_KEY", ""))

    # ── 1. Progressive 5-Level Hint Generation ─────────────────────────────────

    def get_progressive_hints(
        self,
        problem_id: str,
        code: str = "",
        thinking_state: str = "surface_thinking",
        problem_description: str = "",
    ) -> list[dict]:
        """
        Generate 5 distinct levels of hints (Conceptual -> Directional -> DS/Algo -> Detailed -> Near-Solution).
        """
        base_hints = predict_hints_local(
            problem_id=problem_id,
            code=code,
            thinking_state=thinking_state,
            problem_description=problem_description,
        )

        h1 = base_hints[0] if len(base_hints) > 0 else "Focus on understanding what single piece of information is needed at each step."
        h2 = base_hints[1] if len(base_hints) > 1 else "Consider if checking previously seen items avoids redundant work."
        h3 = base_hints[2] if len(base_hints) > 2 else "Think about storing values in a HashMap or array lookup table for O(1) access."

        return [
            {
                "level": 1,
                "title": "Level 1 — Conceptual Hint",
                "hint": f"Concept: {h1}",
                "unlocked": False,
            },
            {
                "level": 2,
                "title": "Level 2 — Directional Hint",
                "hint": f"Direction: {h2}",
                "unlocked": False,
            },
            {
                "level": 3,
                "title": "Level 3 — Data Structure / Algorithm Hint",
                "hint": f"Data Structure: {h3}",
                "unlocked": False,
            },
            {
                "level": 4,
                "title": "Level 4 — Detailed Approach Breakdown",
                "hint": f"Approach: For problem '{problem_id}', iterate through the input while maintaining state in an auxiliary memory structure. Check target conditions at each iteration.",
                "unlocked": False,
            },
            {
                "level": 5,
                "title": "Level 5 — Near-Solution Guidance",
                "hint": f"Guidance: Write a loop `for i, num in enumerate(nums)`. Calculate required complement, check if `complement in seen`. If found return indices; else store `seen[num] = i`.",
                "unlocked": False,
            },
        ]

    # ── 2. Next-Step Bridge Feature ───────────────────────────────────────────

    def get_bridge_options(
        self,
        thought: str = "",
        code: str = "",
        problem_id: str = "unknown",
        problem_title: str = "DSA Problem",
        problem_description: str = "",
    ) -> list[dict]:
        """
        Generates 3 next-step options (solid, exploratory, risky) with non-guaranteed correctness.
        """
        return generate_bridge_options(
            user_thought=thought,
            code=code,
            problem_id=problem_id,
            problem_title=problem_title,
            problem_description=problem_description,
        )

    def get_next_steps(
        self,
        thought: str,
        problem_id: str = "unknown",
        thinking_state: str = "surface_thinking",
        problem_description: str = "",
    ) -> list[str]:
        return predict_next_steps_local(
            user_input=thought,
            problem_id=problem_id,
            thinking_state=thinking_state,
            problem_description=problem_description,
        )

    # ── 3. Mentor Service Pipeline Methods ─────────────────────────────────────

    def understand_problem(
        self, problem_id: str, title: str, statement: str, constraints: str = ""
    ) -> dict:
        return mentor_service.understand_problem(
            problem_id=problem_id, title=title, statement=statement, constraints=constraints
        )

    def pattern_hint(
        self, problem_id: str, title: str, user_thoughts: str = "", code_draft: str = ""
    ) -> dict:
        return mentor_service.pattern_hint(
            problem_id=problem_id, title=title, user_thoughts=user_thoughts, code_draft=code_draft
        )

    def review_code(
        self, problem_id: str, code: str, language: str = "python", test_results: dict = None
    ) -> dict:
        return mentor_service.review_code(
            problem_id=problem_id, code=code, language=language, test_results=test_results
        )

    # ── 4. Thinking State & Understanding Evaluation ───────────────────────────

    def evaluate_understanding(
        self,
        text: str,
        problem_id: str = "unknown",
        problem_description: str = "",
    ) -> dict:
        return predict_understanding_local(
            text=text,
            problem_id=problem_id,
            problem_description=problem_description,
        )

    # ── 5. Deep Pseudocode Evaluation ──────────────────────────────────────────

    def evaluate_pseudocode(self, code: str, problem_description: str = "") -> dict:
        local_res = predict_pseudo_local(code)
        label = local_res.get("label", "brute_force")

        if label == "optimal":
            feedback = "Excellent! Your approach uses optimal time and space complexity."
            time_comp = "O(n)"
            space_comp = "O(n)"
            issues = []
            suggestions = ["Consider potential boundary conditions (empty input, duplicates)."]
        elif label == "better":
            feedback = "Good improvement! Your algorithm is better than brute force but can be refined further."
            time_comp = "O(n log n)"
            space_comp = "O(1)"
            issues = ["Slight overhead in sort or search step."]
            suggestions = ["Check if a hashmap or two-pointer approach eliminates the sorting log n factor."]
        elif label == "brute_force":
            feedback = "This is a brute-force approach. It works correctly for small inputs, but time complexity is high."
            time_comp = "O(n²)"
            space_comp = "O(1)"
            issues = ["Nested iteration causes high time complexity O(n²)."]
            suggestions = ["Store seen elements in a HashMap to check complements in O(1) time."]
        else:
            feedback = "The pseudocode appears to have logical or structural issues."
            time_comp = "Unknown"
            space_comp = "Unknown"
            issues = ["Incomplete loop boundary or missing return condition."]
            suggestions = ["Ensure all loop indices and return paths are defined."]

        return {
            "status": "success",
            "label": label,
            "feedback": feedback,
            "approach": f"Identified approach: {label.replace('_', ' ').title()}",
            "correctness": "Logically sound" if label in ["optimal", "better", "brute_force"] else "Needs revision",
            "efficiency": "Optimal" if label == "optimal" else "Suboptimal",
            "issues": issues,
            "suggestions": suggestions,
            "time_complexity": time_comp,
            "space_complexity": space_comp,
        }

    # ── 6. Personalization & Problem Recommendations ─────────────────────────

    def recommend_problems(self, weak_topics: list[str], solved_ids: list[str]) -> list[dict]:
        all_recs = [
            {
                "id": "valid-parentheses",
                "title": "Valid Parentheses",
                "difficulty": "Easy",
                "category": "Stacks",
                "tags": ["Stack", "String"],
                "reasoning": "Targeted practice for Stack operations & order matching",
            },
            {
                "id": "binary-search",
                "title": "Binary Search",
                "difficulty": "Easy",
                "category": "Searching",
                "tags": ["Binary Search", "Array"],
                "reasoning": "Master logarithmic divide-and-conquer searching",
            },
            {
                "id": "bfs",
                "title": "Breadth First Search (BFS)",
                "difficulty": "Medium",
                "category": "Graphs",
                "tags": ["Graph", "BFS", "Queue"],
                "reasoning": "Strengthen graph traversal & queue frontier logic",
            },
            {
                "id": "fibonacci-dp",
                "title": "Fibonacci Numbers (DP)",
                "difficulty": "Easy",
                "category": "Dynamic Programming",
                "tags": ["Dynamic Programming", "Recursion"],
                "reasoning": "Build foundation in DP tabulation & state transitions",
            },
        ]

        filtered = [r for r in all_recs if r["id"] not in solved_ids]
        return filtered[:2] if filtered else all_recs[:2]


ai_service = AIService()

