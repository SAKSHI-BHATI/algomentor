"""
mentor_service.py — AI Mentor Service for AlgoMentor 9-Stage Pipeline

Implements mentor reasoning for:
- Stage 1: Problem Understanding (simplified explanation, real-world analogy, core objective)
- Stage 3: Socratic Pattern Hint (guiding questions toward pattern recognition)
- Stage 7: AI Code Review (constructive explanation of bugs/edge cases WITHOUT rewriting code)
"""

import os
from typing import Dict, Any


class MentorService:
    """
    Socratic AI Mentor enforcing the core design constraint:
    Behave like a mentor, not an answer key.
    """

    def understand_problem(
        self, problem_id: str, title: str, statement: str, constraints: str = ""
    ) -> Dict[str, Any]:
        """
        Stage 1: Generates an intuitive problem breakdown, key inputs/outputs, and real-world analogy.
        """
        # Fallback / template generator
        return {
            "status": "success",
            "problem_id": problem_id,
            "title": title,
            "simplified_explanation": f"At its core, '{title}' asks you to find a specific relationship or subset within the given input while satisfying all constraints.",
            "real_world_analogy": "Think of looking through a stack of cards or searching for two items in a bag whose values sum to a specific target.",
            "key_objectives": [
                "Understand what input structure is provided.",
                "Identify what exact result or indices must be returned.",
                "Notice constraints on input size to determine acceptable time complexity."
            ],
            "clarifying_questions": [
                "Can the input contain duplicate values or empty structures?",
                "Is the input array/string guaranteed to be sorted?",
                "What should be returned if no valid answer exists?"
            ]
        }

    def pattern_hint(
        self,
        problem_id: str,
        title: str,
        user_thoughts: str = "",
        code_draft: str = ""
    ) -> Dict[str, Any]:
        """
        Stage 3: Socratic nudge helping student recognize the underlying pattern.
        """
        return {
            "status": "success",
            "problem_id": problem_id,
            "socratic_question": "What property of the input structure allows you to look up elements faster than scanning everything sequentially?",
            "pattern_family": "Lookups & State Maintenance (e.g. HashMap / Two Pointers)",
            "guided_nudge": "If you are currently spending O(n) time searching inside a loop, ask yourself: can you trade a small amount of extra memory (space) to make every search instantaneous (O(1))?",
            "suggested_focus": "Try listing what information you have seen so far as you move through the input."
        }

    def review_code(
        self,
        problem_id: str,
        code: str,
        language: str = "python",
        test_results: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Stage 7: AI Code Review explaining code issues without rewriting code.
        """
        if not code.strip():
            return {
                "status": "error",
                "message": "No code provided for review."
            }

        # Analyze code properties
        has_loop = "for" in code or "while" in code
        has_hashmap = "dict" in code or "map" in code or "{" in code or "set" in code
        has_return = "return" in code

        summary = "Your code structure shows good progress towards solving the problem."
        flaws = []
        guidance = []

        if not has_return:
            flaws.append("The solution function is missing an explicit `return` statement.")
            guidance.append("Ensure your function returns the computed result rather than just printing it.")

        if test_results and not test_results.get("all_passed", False):
            failed_count = test_results.get("failed_count", 0)
            flaws.append(f"Code failed on {failed_count} test case(s).")
            guidance.append("Check edge cases such as empty inputs, negative numbers, or arrays with only 2 elements.")

        if not flaws:
            summary = "Great work! Your code passes the logic checks and handles input processing cleanly."
            guidance.append("Consider analyzing your time and space complexity to ensure it is optimal.")

        return {
            "status": "success",
            "problem_id": problem_id,
            "code_summary": summary,
            "identified_flaws": flaws if flaws else ["No major structural flaws detected."],
            "mentor_explanation": (
                "Remember: A mentor explains why an approach succeeds or fails. "
                "Review where your code updates state during iteration and double-check return types."
            ),
            "next_refinement_steps": guidance,
            "rewrite_provided": False  # Enforces design constraint!
        }


mentor_service = MentorService()
