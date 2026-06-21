from __future__ import annotations

import re
from typing import Any


def predict(code: Any) -> dict[str, str]:
    """Evaluates pseudocode string and returns complexity label."""
    code_str = str(code or "").strip()

    if len(code_str) < 15:
        return {"label": "incorrect"}

    lines = [line.strip().lower() for line in code_str.splitlines() if line.strip()]

    # Look for loop structures
    loop_keywords = ["for ", "for each", "while ", "repeat "]
    loops = [i for i, line in enumerate(lines) if any(line.startswith(k) for k in loop_keywords)]

    # Check for nested loops (heuristic: multiple loops with different indentations, or multiple nested statements)
    has_nested_loops = False
    if len(loops) >= 2:
        # Check if one loop is inside another by checking indentation in raw lines
        raw_lines = [line for line in code_str.splitlines() if line.strip()]
        for idx in range(len(raw_lines) - 1):
            curr_line = raw_lines[idx]
            curr_indent = len(curr_line) - len(curr_line.lstrip(" "))
            if any(curr_line.strip().lower().startswith(k) for k in loop_keywords):
                # Search ahead for another loop with greater indentation
                for next_idx in range(idx + 1, len(raw_lines)):
                    next_line = raw_lines[next_idx]
                    next_indent = len(next_line) - len(next_line.lstrip(" "))
                    if next_indent > curr_indent and any(
                        next_line.strip().lower().startswith(k) for k in loop_keywords
                    ):
                        has_nested_loops = True
                        break
                    if next_indent <= curr_indent:
                        # Left the first loop block
                        break

    # Look for optimization structures
    optimized_structures = ["map", "dict", "hash", "seen", "set", "memo", "dp", "table", "stack", "queue"]
    code_lower = code_str.lower()
    uses_optimal_ds = any(ds in code_lower for ds in optimized_structures)
    uses_two_pointers = "pointer" in code_lower or ("left" in code_lower and "right" in code_lower)

    # Basic recursion checks
    is_recursive = False
    # Check if a function is defined and called within itself (crude heuristic)
    func_match = re.search(r"(?:def|function)\s+(\w+)", code_lower)
    if func_match:
        func_name = func_match.group(1)
        # Check if function name appears again in the code body
        if code_lower.count(func_name) >= 2:
            is_recursive = True

    # Final evaluation logic
    if has_nested_loops:
        # If they use a hashmap inside a nested loop, it's probably "better" but not optimal
        if uses_optimal_ds:
            return {"label": "better"}
        return {"label": "brute_force"}

    if uses_optimal_ds or uses_two_pointers:
        if is_recursive and not ("memo" in code_lower or "dp" in code_lower):
            # Recursion without memoization is usually slow
            return {"label": "better"}
        return {"label": "optimal"}

    if len(loops) == 1:
        # Single loop is generally better than brute force, but might not be optimal
        # depending on if the problem needs O(1) checks (like Two Sum)
        return {"label": "better"}

    if is_recursive and not ("memo" in code_lower or "dp" in code_lower):
        return {"label": "brute_force"}

    # Fallback to better if it looks like some code but doesn't meet optimal criteria
    return {"label": "better"}
