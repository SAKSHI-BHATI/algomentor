"""
bridge_model.py — Bridge Next-Step Model for AlgoMentor

Generates 3 next-step options for a student who is stuck or planning their approach.
Crucial constraint: Deliberately, NOT all 3 options are guaranteed to lead to a correct solution.
Options are tagged with confidence:
- "solid": Optimal / correct strategic path
- "exploratory": Plausible path that might be suboptimal or require pivot
- "risky": Misleading / dead-end path (promotes critical evaluation)
"""

import os
import json
from typing import List, Dict, Any


def generate_bridge_options(
    user_thought: str = "",
    code: str = "",
    problem_id: str = "unknown",
    problem_title: str = "DSA Problem",
    problem_description: str = "",
    pattern: str = "General",
) -> List[Dict[str, Any]]:
    """
    Returns 3 distinct next-step options for student evaluation.
    """
    thought_lower = user_thought.lower()
    code_lower = code.lower()

    # Problem-specific custom fallback options if offline
    if "sum" in problem_id or "two" in problem_id or "array" in problem_id:
        return [
            {
                "id": "opt-1",
                "title": "Use a HashMap / Dictionary to track complements",
                "description": "Store each element's value and index while iterating. For each number x, check if (target - x) is already in the map.",
                "confidence": "solid",
                "leads_to_solution": True,
                "mentor_insight": "Reduces lookup time from O(n) to O(1), achieving optimal O(n) overall time complexity."
            },
            {
                "id": "opt-2",
                "title": "Sort the array first, then use two pointers",
                "description": "Sort the input numbers in ascending order and place left pointer at 0 and right pointer at len - 1.",
                "confidence": "exploratory",
                "leads_to_solution": True,
                "mentor_insight": "Sorting takes O(n log n). If original indices are needed, you must track original indices before sorting."
            },
            {
                "id": "opt-3",
                "title": "Use nested loops to check all possible index pairs",
                "description": "Compare every element i with every element j (where j > i) and check if nums[i] + nums[j] == target.",
                "confidence": "risky",
                "leads_to_solution": False,
                "mentor_insight": "This brute-force approach works for tiny arrays, but will Time Out (TLE) on large inputs due to O(n²) time complexity."
            }
        ]
    elif "bfs" in problem_id or "graph" in problem_id or "tree" in problem_id:
        return [
            {
                "id": "opt-1",
                "title": "Use a Queue and a Visited Set for level-by-level traversal",
                "description": "Push start node to Queue and Visited. While Queue is not empty, pop front, process, and push unvisited neighbors.",
                "confidence": "solid",
                "leads_to_solution": True,
                "mentor_insight": "Ensures shortest path in unweighted graphs and guarantees all nodes at distance k are visited before distance k+1."
            },
            {
                "id": "opt-2",
                "title": "Use Depth-First Search (DFS) with a Recursion Stack",
                "description": "Recursively explore each path as deep as possible before backtracking.",
                "confidence": "exploratory",
                "leads_to_solution": True,
                "mentor_insight": "Works for graph connectivity, but requires extra handling if looking for shortest path in unweighted graph."
            },
            {
                "id": "opt-3",
                "title": "Iterate nodes with a simple array without tracking visited state",
                "description": "Loop over nodes array and process neighbor nodes in sequential order.",
                "confidence": "risky",
                "leads_to_solution": False,
                "mentor_insight": "Without a Visited tracking set, cyclic graphs will cause infinite loops!"
            }
        ]

    # Generic high-quality 3 options
    return [
        {
            "id": "opt-1",
            "title": "Decompose into smaller subproblems & identify state",
            "description": "Break down the main constraint into sub-conditions and check which data structure accelerates lookups.",
            "confidence": "solid",
            "leads_to_solution": True,
            "mentor_insight": "Focusing on data structure efficiency (e.g. HashMap, Stack, Two-Pointers) often drops time complexity significantly."
        },
        {
            "id": "opt-2",
            "title": "Pre-process or sort the input data before processing",
            "description": "Re-order elements or transform input to establish monotonicity.",
            "confidence": "exploratory",
            "leads_to_solution": True,
            "mentor_insight": "Sorting helps two-pointer or binary search approaches, but check if sorting alters required output order."
        },
        {
            "id": "opt-3",
            "title": "Generate all possible combinations using greedy choice",
            "description": "Pick the locally optimal choice at each step without validating global constraints.",
            "confidence": "risky",
            "leads_to_solution": False,
            "mentor_insight": "Greedy choices without optimal substructure proof often fail on boundary test cases!"
        }
    ]
