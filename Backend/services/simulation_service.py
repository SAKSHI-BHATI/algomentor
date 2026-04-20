"""
simulation_service.py  —  AlgoMentor Backend
=============================================
All algorithm simulation logic extracted from the Streamlit visualizer.
Zero Streamlit dependencies — pure Python generators and tracing utilities.

Public surface:
    run_simulation(problem_id, code, input_data, use_optimal) -> dict
        Returns {"steps": [...], "is_graph": bool}

Each step dict:
    {
        "state":     list,        # current array / node-visit order
        "idx1":      int,         # primary pointer (-1 = none)
        "idx2":      int,         # secondary pointer (-1 = none)
        "message":   str,
        "is_action": bool,        # True = swap/visit highlight
        # graph-only extras (omitted for array steps):
        "is_graph":        bool,
        "current_node":    int | str,
        "frontier":        list,
        "visited":         list,
        "graph":           dict,
    }
"""

from __future__ import annotations

import re
import sys
import ast
from collections import deque
from typing import Any, Iterator

import numpy as np


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def emit_step(
    state=None,
    idx1: int = -1,
    idx2: int = -1,
    message: str = "",
    is_action: bool = False,
    **extra,
) -> dict:
    """Build a normalised step payload."""
    payload = {
        "state":     list(state) if state is not None else [],
        "idx1":      idx1,
        "idx2":      idx2,
        "message":   message,
        "is_action": is_action,
    }
    payload.update(extra)
    return payload


def _swap(arr: list, i: int, j: int) -> None:
    arr[i], arr[j] = arr[j], arr[i]


# ═══════════════════════════════════════════════════════════════════════════════
# SORTING GENERATORS
# ═══════════════════════════════════════════════════════════════════════════════

def bubble_sort_visualizer(arr: list) -> Iterator[dict]:
    n = len(arr)
    yield emit_step(list(arr), -1, -1, "Starting Bubble Sort")
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            yield emit_step(list(arr), j, j + 1,
                            f"Comparing {arr[j]} and {arr[j+1]}", False)
            if arr[j] > arr[j + 1]:
                _swap(arr, j, j + 1)
                swapped = True
                yield emit_step(list(arr), j, j + 1, "Swapping elements", True)
        if not swapped:
            break
    yield emit_step(list(arr), -1, -1, "Array Sorted!", True)


def selection_sort_visualizer(arr: list) -> Iterator[dict]:
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            yield emit_step(list(arr), min_idx, j,
                            f"Comparing min with {arr[j]}", False)
            if arr[j] < arr[min_idx]:
                min_idx = j
                yield emit_step(list(arr), min_idx, -1,
                                f"New minimum: {arr[min_idx]}", False)
        _swap(arr, i, min_idx)
        yield emit_step(list(arr), i, -1,
                        f"Placed {arr[i]} at index {i}", True)
    yield emit_step(list(arr), -1, -1, "Sort Complete", True)


def insertion_sort_visualizer(arr: list) -> Iterator[dict]:
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        yield emit_step(list(arr), i, j, f"Picking key: {key}", False)
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
            yield emit_step(list(arr), j + 1, -1, "Shifting element right", True)
        arr[j + 1] = key
        yield emit_step(list(arr), j + 1, -1, f"Inserted {key}", False)
    yield emit_step(list(arr), -1, -1, "Sort Complete", True)


# ═══════════════════════════════════════════════════════════════════════════════
# SEARCHING GENERATORS
# ═══════════════════════════════════════════════════════════════════════════════

def linear_search_visualizer(arr: list, target: Any) -> Iterator[dict]:
    for i, val in enumerate(arr):
        yield emit_step(list(arr), i, -1, f"Checking index {i}: {val}", False)
        if val == target:
            yield emit_step(list(arr), i, -1, f"Found {target}!", True)
            return
    yield emit_step(list(arr), -1, -1, "Target not found", False)


def binary_search_visualizer(arr: list, target: Any) -> Iterator[dict]:
    low, high = 0, len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        yield emit_step(list(arr), mid, -1,
                        f"Range: [{low}, {high}], Mid: {arr[mid]}", False)
        if arr[mid] == target:
            yield emit_step(list(arr), mid, -1,
                            f"Found {target} at index {mid}!", True)
            return
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    yield emit_step(list(arr), -1, -1, "Target not found", False)


# ═══════════════════════════════════════════════════════════════════════════════
# BASIC ALGORITHM GENERATORS
# ═══════════════════════════════════════════════════════════════════════════════

def two_sum_visualizer(nums: list, target: int) -> Iterator[dict]:
    hashmap: dict = {}
    yield emit_step(list(nums), -1, -1,
                    f"Searching for two numbers that sum to {target}", False)
    for i, num in enumerate(nums):
        complement = target - num
        yield emit_step(list(nums), i, -1,
                        f"Current: {num}. Need complement: {complement}", False)
        if complement in hashmap:
            yield emit_step(list(nums), i, hashmap[complement],
                            f"Found! {num} + {complement} = {target}", True)
            return
        hashmap[num] = i
    yield emit_step(list(nums), -1, -1, "No solution found", False)


def valid_parentheses_visualizer(s: str) -> Iterator[dict]:
    stack: list = []
    pairs = {")": "(", "]": "[", "}": "{"}
    chars = list(s)
    for i, ch in enumerate(chars):
        yield emit_step(stack + ["|"] + chars[i:], i, -1,
                        f"Processing: {ch}", False)
        if ch in "([{":
            stack.append(ch)
        else:
            if not stack or stack[-1] != pairs[ch]:
                yield emit_step(stack + ["|"] + chars[i:], i, -1,
                                "Mismatch! Invalid.", True)
                return
            stack.pop()
    valid = not stack
    yield emit_step(stack, -1, -1,
                    "Stack empty! Valid." if valid else "Stack not empty! Invalid.",
                    True)


def fibonacci_dp_visualizer(n: int) -> Iterator[dict]:
    dp = [0] * (n + 1)
    if n >= 1:
        dp[1] = 1
    yield emit_step(dp[:], -1, -1, "Initialized DP table", False)
    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
        yield emit_step(dp[:], i, -1,
                        f"dp[{i}] = dp[{i-1}] + dp[{i-2}] = {dp[i]}", False)
    yield emit_step(dp[:], -1, -1, f"Fibonacci({n}) is {dp[n]}", True)


def reverse_linked_list_visualizer(arr: list) -> Iterator[dict]:
    prev: list = []
    curr = list(arr)
    yield emit_step(curr[:], -1, -1, "Starting reversal", False)
    while curr:
        node = curr.pop(0)
        prev = [node] + prev
        yield emit_step(prev + ["→"] + curr, -1, -1,
                        f"Moving {node} to front", False)
    yield emit_step(prev[:], -1, -1, "Reversal complete", True)


# ═══════════════════════════════════════════════════════════════════════════════
# GRAPH GENERATORS
# ═══════════════════════════════════════════════════════════════════════════════

def _graph_step(order, current_node, frontier, visited_set, message, is_action):
    """Helper: build a graph step with all required fields."""
    return {
        "state":        list(order),
        "idx1":         current_node if is_action else -1,
        "idx2":         -1,
        "message":      message,
        "is_action":    is_action,
        "is_graph":     True,
        "current_node": current_node,
        "frontier":     list(frontier),
        "visited":      list(visited_set),
    }


def bfs_visualizer(graph: dict, start: int = 0) -> Iterator[dict]:
    visited = {start}
    queue = deque([start])
    order: list = []
    yield _graph_step(order, start, list(queue), visited,
                      f"Starting BFS from node {start}. Queue: {list(queue)}", False)
    while queue:
        node = queue.popleft()
        order.append(node)
        yield _graph_step(order, node, list(queue), visited,
                          f"Visiting node {node}. Order: {order}", True)
        added = []
        for nbr in graph.get(node, []):
            if nbr not in visited:
                visited.add(nbr)
                queue.append(nbr)
                added.append(nbr)
        if added:
            yield _graph_step(order, node, list(queue), visited,
                              f"Added to queue: {added}. Queue: {list(queue)}", False)
    yield _graph_step(order, -1, [], visited,
                      f"BFS Complete! Traversal order: {order}", True)


def dfs_visualizer(graph: dict, start: int = 0) -> Iterator[dict]:
    visited: set = set()
    stack = [start]
    order: list = []
    yield _graph_step(order, start, stack[:], visited,
                      f"Starting DFS from node {start}. Stack: {stack}", False)
    while stack:
        node = stack.pop()
        if node in visited:
            yield _graph_step(order, node, stack[:], visited,
                              f"Node {node} already visited, skipping.", False)
            continue
        visited.add(node)
        order.append(node)
        yield _graph_step(order, node, stack[:], visited,
                          f"Visiting node {node}. Order: {order}", True)
        added = []
        for nbr in reversed(graph.get(node, [])):
            if nbr not in visited:
                stack.append(nbr)
                added.append(nbr)
        if added:
            yield _graph_step(order, node, stack[:], visited,
                              f"Pushed to stack: {added}. Stack: {stack}", False)
    yield _graph_step(order, -1, [], visited,
                      f"DFS Complete! Traversal order: {order}", True)


# ═══════════════════════════════════════════════════════════════════════════════
# OPTIMAL SOLUTION GENERATORS  (used when use_optimal=True)
# ═══════════════════════════════════════════════════════════════════════════════

_OPTIMAL_INPUTS: dict[str, dict] = {
    "two_sum":          {"nums": [2, 7, 11, 15], "target": 9},
    "valid_parentheses": {"s": "({[]})"},
    "longest_substring": {"s": "abcabcbb"},
    "climbing_stairs":   {"n": 6},
    "reverse_linked_list": {"arr": [1, 2, 3, 4, 5]},
    "binary_search":     {"arr": [1, 3, 5, 7, 9, 11], "target": 7},
    "maximum_subarray":  {"arr": [-2, 1, -3, 4, -1, 2, 1, -5, 4]},
    "contains_duplicate": {"arr": [1, 2, 3, 1]},
}


def _longest_substring_optimal(s: str) -> Iterator[dict]:
    left = 0
    char_idx: dict = {}
    max_len = 0
    arr = list(s)
    yield emit_step(arr, -1, -1, "Starting sliding window", False)
    for right in range(len(s)):
        if s[right] in char_idx and char_idx[s[right]] >= left:
            left = char_idx[s[right]] + 1
        char_idx[s[right]] = right
        win = list(s[left: right + 1])
        max_len = max(max_len, right - left + 1)
        yield emit_step(arr, right, left,
                        f"Window [{left},{right}] = {''.join(win)}, len={right-left+1}",
                        right - left + 1 > max_len - 1)
    yield emit_step(arr, -1, -1, f"Longest substring length: {max_len}", True)


def _max_subarray_optimal(arr: list) -> Iterator[dict]:
    curr = arr[0]
    best = arr[0]
    yield emit_step(list(arr), 0, -1, f"Init: curr={curr}, best={best}", False)
    for i in range(1, len(arr)):
        prev_curr = curr
        curr = max(arr[i], curr + arr[i])
        best = max(best, curr)
        yield emit_step(list(arr), i, -1,
                        f"max({arr[i]}, {prev_curr}+{arr[i]})={curr}, best={best}",
                        curr == arr[i])
    yield emit_step(list(arr), -1, -1, f"Maximum subarray sum: {best}", True)


def _contains_duplicate_optimal(arr: list) -> Iterator[dict]:
    seen: set = set()
    yield emit_step(list(arr), -1, -1, "Init empty set", False)
    for i, val in enumerate(arr):
        yield emit_step(list(arr), i, -1, f"Checking {val} in seen set", False)
        if val in seen:
            yield emit_step(list(arr), i, -1, f"Duplicate Found: {val}!", True)
            return
        seen.add(val)
    yield emit_step(list(arr), -1, -1, "No duplicates found", True)


# ═══════════════════════════════════════════════════════════════════════════════
# CUSTOM CODE TRACER  (sys.settrace-based — from Streamlit)
# ═══════════════════════════════════════════════════════════════════════════════

def _is_simple_sequence(value: Any) -> bool:
    simple_types = (int, float, str, bool)
    return (
        isinstance(value, (list, tuple, deque))
        and all(isinstance(item, simple_types) for item in value)
    )


def infer_state_sequence(local_vars: dict) -> list:
    preferred = ("arr", "array", "nums", "data", "values", "items",
                 "lst", "list1", "result", "output")
    for name in preferred:
        val = local_vars.get(name)
        if _is_simple_sequence(val):
            return list(val)
    for val in local_vars.values():
        if _is_simple_sequence(val):
            return list(val)
    simple_types = (int, float, str, bool)
    return [
        f"{k}={v}"
        for k, v in local_vars.items()
        if isinstance(v, simple_types) and k != "__builtins__"
    ][:12]


def infer_pointer_indexes(local_vars: dict) -> tuple[int, int]:
    i_names = ("i", "left", "low", "start", "ptr1")
    j_names = ("j", "right", "high", "end", "ptr2")
    idx1, idx2 = -1, -1
    for name in i_names:
        v = local_vars.get(name)
        if isinstance(v, int):
            idx1 = v
            break
    for name in j_names:
        v = local_vars.get(name)
        if isinstance(v, int):
            idx2 = v
            break
    return idx1, idx2


def is_adjacency_graph(value: Any) -> bool:
    if not isinstance(value, dict) or not value:
        return False
    for key, neighbours in list(value.items())[:8]:
        if not isinstance(key, (int, str)):
            return False
        if not isinstance(neighbours, (list, tuple, set, deque)):
            return False
        if any(not isinstance(n, (int, str)) for n in list(neighbours)[:12]):
            return False
    return True


def infer_graph_trace_payload(local_vars: dict) -> dict | None:
    graph = None
    for key in ("graph", "adj", "adj_list", "adjacency", "adjacency_list", "g"):
        val = local_vars.get(key)
        if is_adjacency_graph(val):
            graph = {node: list(nbrs) for node, nbrs in val.items()}
            break
    if graph is None:
        for val in local_vars.values():
            if is_adjacency_graph(val):
                graph = {node: list(nbrs) for node, nbrs in val.items()}
                break
    if graph is None:
        return None

    current_node: int | str = -1
    for key in ("current_node", "node", "curr", "u", "v", "vertex", "src"):
        val = local_vars.get(key)
        if isinstance(val, (int, str)):
            current_node = val
            break

    frontier: list = []
    for key in ("queue", "stack", "frontier", "q"):
        val = local_vars.get(key)
        if isinstance(val, (list, tuple, deque)):
            frontier = list(val)
            break

    raw_visited = local_vars.get("visited", set())
    visited_set = set(raw_visited) if isinstance(raw_visited, (set, list, tuple, deque)) else set()

    state: list = []
    for key in ("order", "path", "result", "traversal", "bfs_order", "dfs_order", "answer"):
        val = local_vars.get(key)
        if isinstance(val, (list, tuple, deque)):
            state = list(val)
            break
    if not state and visited_set:
        state = list(visited_set)

    if current_node == -1 and not frontier and not visited_set and not state:
        return None

    return {
        "graph":        graph,
        "state":        state,
        "current_node": current_node,
        "frontier":     frontier,
        "visited":      list(visited_set),
        "is_graph":     True,
    }


def normalize_custom_array_step(step: Any, last_state: list) -> tuple:
    if isinstance(step, dict):
        state     = step.get("state", last_state)
        idx1      = step.get("idx1", -1)
        idx2      = step.get("idx2", -1)
        message   = str(step.get("message", "Custom step"))
        is_action = bool(step.get("is_action", False))
    elif isinstance(step, (list, tuple)) and len(step) == 5:
        state, idx1, idx2, message, is_action = step
    else:
        raise ValueError("Step must be emit_step() dict or 5-item tuple.")
    return list(state), int(idx1), int(idx2), str(message), bool(is_action)


def normalize_custom_graph_step(step: Any, last_state: list) -> dict:
    if isinstance(step, dict):
        state        = step.get("state", step.get("order", last_state))
        current_node = step.get("current_node", step.get("node", -1))
        frontier     = list(step.get("frontier", []))
        visited      = set(step.get("visited", state or []))
        message      = str(step.get("message", "Custom graph step"))
        is_action    = bool(step.get("is_action", False))
        graph        = step.get("graph", {})
    elif isinstance(step, (list, tuple)) and len(step) == 5:
        state, current_node, _, message, is_action = step
        frontier, visited, graph = [], set(), {}
    else:
        raise ValueError("Graph step must be emit_step() dict or 5-item tuple.")
    return {
        "state":        list(state) if state else [],
        "current_node": current_node if current_node is not None else -1,
        "frontier":     frontier,
        "visited":      list(visited),
        "message":      message,
        "is_action":    is_action,
        "graph":        graph,
        "is_graph":     True,
    }


def trace_plain_python_code(user_code: str, runtime_inputs: dict) -> tuple[list, str | None]:
    """
    Execute arbitrary Python using sys.settrace to capture line-by-line steps.
    Returns (steps_list, error_string | None).
    """
    filename = "<custom_exec>"
    source_lines = user_code.splitlines()
    steps: list[dict] = []

    namespace = {
        "deque":     deque,
        "np":        np,
        "re":        re,
        "emit_step": emit_step,
    }
    namespace.update(runtime_inputs)

    def make_message(lineno: int) -> str:
        text = source_lines[lineno - 1].strip() if 0 < lineno <= len(source_lines) else ""
        return f"Line {lineno}: {text}" if text else f"Line {lineno}"

    def tracer(frame, event, _arg):
        if frame.f_code.co_filename != filename:
            return tracer
        if event == "line":
            local_vars = dict(frame.f_locals)
            graph_payload = infer_graph_trace_payload(local_vars)
            if graph_payload is not None:
                steps.append({
                    **graph_payload,
                    "idx1":     -1,
                    "idx2":     -1,
                    "message":  make_message(frame.f_lineno),
                    "is_action": True,
                    "line_no":  frame.f_lineno,
                })
            else:
                state        = infer_state_sequence(local_vars)
                idx1, idx2   = infer_pointer_indexes(local_vars)
                steps.append({
                    "state":    state,
                    "idx1":     idx1,
                    "idx2":     idx2,
                    "message":  make_message(frame.f_lineno),
                    "is_action": True,
                    "line_no":  frame.f_lineno,
                    "is_graph": False,
                })
        return tracer

    try:
        compiled = compile(user_code, filename, "exec")
        prev_tracer = sys.gettrace()
        sys.settrace(tracer)
        try:
            exec(compiled, namespace, namespace)     # noqa: S102
        finally:
            sys.settrace(prev_tracer)
    except SyntaxError as exc:
        return [], f"SyntaxError on line {exc.lineno}: {exc.msg}"
    except Exception as exc:
        tb = exc.__traceback__
        target_tb = None
        while tb is not None:
            if tb.tb_frame.f_code.co_filename == filename:
                target_tb = tb
            tb = tb.tb_next
        lineno = target_tb.tb_lineno if target_tb else len(source_lines)
        line_text = (source_lines[lineno - 1].strip()
                     if 0 < lineno <= len(source_lines) else "")
        steps.append({
            "state":     infer_state_sequence(
                dict(target_tb.tb_frame.f_locals) if target_tb else {}),
            "idx1":      -1,
            "idx2":      -1,
            "message":   f"Error at line {lineno}: {line_text} ({exc})",
            "is_action": False,
            "is_graph":  False,
        })
        return steps, None

    # Add final completion step
    graph_payload = infer_graph_trace_payload(namespace)
    if graph_payload is not None:
        steps.append({
            **graph_payload,
            "idx1":     -1,
            "idx2":     -1,
            "message":  "Execution complete",
            "is_action": True,
        })
    else:
        steps.append({
            "state":     infer_state_sequence(namespace),
            "idx1":      -1,
            "idx2":      -1,
            "message":   "Execution complete",
            "is_action": True,
            "is_graph":  False,
        })

    return steps, None


# ═══════════════════════════════════════════════════════════════════════════════
# PROBLEM_ID → GENERATOR MAPPING
# ═══════════════════════════════════════════════════════════════════════════════

def _steps_from_generator(gen) -> tuple[list[dict], bool]:
    """Drain a generator into a list of normalised step dicts."""
    steps: list[dict] = []
    is_graph = False
    last_state: list = []

    for raw in gen:
        if isinstance(raw, dict) and raw.get("is_graph"):
            step = normalize_custom_graph_step(raw, last_state)
            is_graph = True
        else:
            state, idx1, idx2, message, is_action = normalize_custom_array_step(
                raw, last_state)
            step = {
                "state":     state,
                "idx1":      idx1,
                "idx2":      idx2,
                "message":   message,
                "is_action": is_action,
                "is_graph":  False,
            }
        last_state = list(step.get("state", last_state))
        steps.append(step)

    return steps, is_graph


def _default_input(problem_id: str, user_input: dict) -> dict:
    """Merge user-supplied input with safe defaults."""
    defaults = _OPTIMAL_INPUTS.get(problem_id, {})
    return {**defaults, **user_input}


# ═══════════════════════════════════════════════════════════════════════════════
# PUBLIC ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def run_simulation(
    problem_id: str,
    code: str = "",
    input_data: dict | None = None,
    use_optimal: bool = False,
) -> dict:
    """
    Main entry point called by ai_routes.py.

    Args:
        problem_id  : e.g. "two_sum", "custom", "bubble_sort"
        code        : user's pseudocode (used when problem_id == "custom")
        input_data  : dict of runtime values, merged with defaults
        use_optimal : if True, run the known-optimal generator for problem_id

    Returns:
        {"steps": [...], "is_graph": bool}
    """
    if input_data is None:
        input_data = {}

    merged = _default_input(problem_id, input_data)

    # ── Custom code path ────────────────────────────────────────
    if problem_id == "custom" and not use_optimal:
        if not code.strip():
            return {"steps": [], "is_graph": False,
                    "error": "No code provided for custom simulation."}
        runtime = {
            "arr":    merged.get("arr", merged.get("nums", [])),
            "target": merged.get("target", 0),
            "graph":  merged.get("graph", {}),
            "start":  merged.get("start", 0),
        }
        steps, err = trace_plain_python_code(code, runtime)
        if err:
            return {"steps": [], "is_graph": False, "error": err}
        is_graph = any(s.get("is_graph") for s in steps)
        return {"steps": steps, "is_graph": is_graph}

    # ── Built-in problem generators ────────────────────────────
    gen = None

    pid = problem_id.replace("-", "_").lower()

    if pid == "two_sum":
        nums   = merged.get("nums", merged.get("arr", [2, 7, 11, 15]))
        target = int(merged.get("target", 9))
        gen = two_sum_visualizer(list(nums), target)

    elif pid == "valid_parentheses":
        s = str(merged.get("s", "({[]})"))
        gen = valid_parentheses_visualizer(s)

    elif pid == "longest_substring":
        s = str(merged.get("s", "abcabcbb"))
        gen = _longest_substring_optimal(s)

    elif pid == "bubble_sort":
        arr = list(merged.get("arr", merged.get("nums", [64, 34, 25, 12, 22])))
        gen = bubble_sort_visualizer(arr)

    elif pid == "selection_sort":
        arr = list(merged.get("arr", [64, 34, 25, 12, 22]))
        gen = selection_sort_visualizer(arr)

    elif pid == "insertion_sort":
        arr = list(merged.get("arr", [64, 34, 25, 12, 22]))
        gen = insertion_sort_visualizer(arr)

    elif pid == "linear_search":
        arr    = list(merged.get("arr", [10, 20, 30, 40, 50]))
        target = merged.get("target", 30)
        gen = linear_search_visualizer(arr, target)

    elif pid == "binary_search":
        arr    = list(merged.get("arr", [1, 3, 5, 7, 9, 11]))
        target = merged.get("target", 7)
        gen = binary_search_visualizer(arr, target)

    elif pid == "fibonacci_dp":
        n = int(merged.get("n", 7))
        gen = fibonacci_dp_visualizer(n)

    elif pid == "reverse_linked_list":
        arr = list(merged.get("arr", merged.get("nums", [1, 2, 3, 4, 5])))
        gen = reverse_linked_list_visualizer(arr)

    elif pid == "maximum_subarray":
        arr = list(merged.get("arr", [-2, 1, -3, 4, -1, 2, 1, -5, 4]))
        gen = _max_subarray_optimal(arr)

    elif pid == "contains_duplicate":
        arr = list(merged.get("arr", [1, 2, 3, 1]))
        gen = _contains_duplicate_optimal(arr)

    elif pid == "bfs":
        graph = merged.get("graph", {0: [1, 2], 1: [0, 3, 4], 2: [0, 5, 6],
                                      3: [1], 4: [1], 5: [2], 6: [2]})
        start = int(merged.get("start", 0))
        gen = bfs_visualizer(graph, start)

    elif pid == "dfs":
        graph = merged.get("graph", {0: [1, 2], 1: [0, 3, 4], 2: [0, 5, 6],
                                      3: [1], 4: [1], 5: [2], 6: [2]})
        start = int(merged.get("start", 0))
        gen = dfs_visualizer(graph, start)

    else:
        # Unknown problem_id — fallback to plain code tracing if code present
        if code.strip():
            runtime = {
                "arr":    merged.get("arr", merged.get("nums", [])),
                "target": merged.get("target", 0),
            }
            steps, err = trace_plain_python_code(code, runtime)
            if err:
                return {"steps": [], "is_graph": False, "error": err}
            is_graph = any(s.get("is_graph") for s in steps)
            return {"steps": steps, "is_graph": is_graph}
        return {"steps": [], "is_graph": False,
                "error": f"Unknown problem_id: '{problem_id}'"}

    steps, is_graph = _steps_from_generator(gen)
    return {"steps": steps, "is_graph": is_graph}
