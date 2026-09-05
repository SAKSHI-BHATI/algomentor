"""
test_executor.py — Automated Tests for Sandboxed Execution Harness
"""

import pytest
from Backend.services.executor import execute_code, validate_python_code_ast, SecurityError


def test_executor_correct_python_solution():
    code = """
def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        diff = target - num
        if diff in seen:
            return [seen[diff], i]
        seen[num] = i
    return []
"""
    test_cases = [
        {"input": {"nums": [2, 7, 11, 15], "target": 9}, "expected": [0, 1]},
        {"input": {"nums": [3, 2, 4], "target": 6}, "expected": [1, 2]},
    ]
    res = execute_code(code, language="python", test_cases=test_cases, entry_function="two_sum")
    assert res["status"] == "success"
    assert res["all_passed"] is True
    assert res["passed_count"] == 2
    assert res["total_count"] == 2


def test_executor_incorrect_python_solution():
    code = """
def two_sum(nums, target):
    return [0, 0]
"""
    test_cases = [
        {"input": {"nums": [2, 7, 11, 15], "target": 9}, "expected": [0, 1]},
    ]
    res = execute_code(code, language="python", test_cases=test_cases, entry_function="two_sum")
    assert res["status"] == "success"
    assert res["all_passed"] is False
    assert res["passed_count"] == 0


def test_executor_security_block_import():
    code = """
import os
def two_sum(nums, target):
    os.system("ls")
    return []
"""
    test_cases = [{"input": {"nums": [2, 7], "target": 9}, "expected": [0, 1]}]
    res = execute_code(code, language="python", test_cases=test_cases, entry_function="two_sum")
    assert res["status"] == "error"
    assert res["error_type"] == "SecurityError"
    assert "strictly forbidden" in res["message"]
