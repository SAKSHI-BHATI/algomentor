"""
test_simulation.py — Unit tests for simulation generators and AST security.
"""

import pytest
from Backend.services.simulation_service import (
    run_simulation,
    validate_ast_safety,
    bubble_sort_visualizer,
    binary_search_visualizer,
    two_sum_visualizer,
    bfs_visualizer,
)


def test_bubble_sort_visualizer():
    arr = [3, 1, 2]
    steps = list(bubble_sort_visualizer(arr))
    assert len(steps) > 0
    assert steps[-1]["message"] == "Array Sorted!"
    assert steps[-1]["state"] == [1, 2, 3]


def test_binary_search_visualizer():
    arr = [1, 3, 5, 7, 9]
    steps = list(binary_search_visualizer(arr, 7))
    assert len(steps) > 0
    assert "Found 7" in steps[-1]["message"]


def test_two_sum_simulation():
    res = run_simulation("two_sum", input_data={"nums": [2, 7, 11, 15], "target": 9})
    assert res.get("success", True)
    assert len(res["steps"]) > 0
    assert not res["is_graph"]


def test_bfs_simulation():
    res = run_simulation("bfs", input_data={"graph": {0: [1], 1: [0]}, "start": 0})
    assert len(res["steps"]) > 0
    assert res["is_graph"]


def test_ast_security_blocks_import():
    user_code = "import os\nos.system('echo hacked')"
    err = validate_ast_safety(user_code)
    assert err is not None
    assert "Security violation" in err


def test_ast_security_blocks_open():
    user_code = "f = open('/etc/passwd')"
    err = validate_ast_safety(user_code)
    assert err is not None
    assert "Security violation" in err


def test_custom_code_execution_safe():
    user_code = """
arr = [4, 2, 1]
n = len(arr)
for i in range(n):
    for j in range(i+1, n):
        if arr[i] > arr[j]:
            arr[i], arr[j] = arr[j], arr[i]
"""
    res = run_simulation("custom", code=user_code)
    assert "error" not in res
    assert len(res["steps"]) > 0
