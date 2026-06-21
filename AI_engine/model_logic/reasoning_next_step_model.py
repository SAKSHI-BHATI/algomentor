from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[2]
DATASET_PATH = BASE_DIR / "Datasets" / "Reasoning_Next_Step_Dataset.json"


@dataclass
class RequestContext:
    problem: str
    user_thought: str
    pseudocode: str
    language: str


def _load_dataset() -> list[dict[str, Any]]:
    if not DATASET_PATH.exists():
        return []

    try:
        data = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []

    return [item for item in data if isinstance(item, dict)]


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def _extract_section(text: str, label: str) -> str:
    pattern = rf"{re.escape(label)}\s*:\s*(.*?)(?=\n[A-Za-z _-]+\s*:|\Z)"
    match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
    return match.group(1).strip() if match else ""


def _detect_language(pseudocode: str) -> str:
    if not pseudocode.strip():
        return "pseudocode"
    return "pseudocode"


def _parse_request(payload: Any) -> RequestContext:
    if isinstance(payload, dict):
        problem = str(payload.get("problem", "")).strip()
        user_thought = str(
            payload.get("user_thought")
            or payload.get("thought")
            or payload.get("explanation")
            or ""
        ).strip()
        pseudocode = str(
            payload.get("pseudocode")
            or payload.get("code")
            or payload.get("attempt")
            or ""
        ).rstrip()
        language = str(payload.get("language", "")).strip().lower()
    else:
        text = str(payload or "")
        problem = _extract_section(text, "problem")
        user_thought = (
            _extract_section(text, "student thought")
            or _extract_section(text, "thought")
            or _extract_section(text, "explanation")
        )
        pseudocode = (
            _extract_section(text, "pseudocode")
            or _extract_section(text, "code")
            or _extract_section(text, "attempt")
        )
        language = _extract_section(text, "language").lower()

        if not problem and text:
            problem = text
        if not user_thought and text and text != problem:
            user_thought = text

    if not language:
        language = _detect_language(pseudocode)

    return RequestContext(
        problem=problem,
        user_thought=user_thought,
        pseudocode=pseudocode,
        language=language or "pseudocode",
    )


def _lines(text: str) -> list[str]:
    return [line.rstrip() for line in text.splitlines() if line.strip()]


def _last_meaningful_line(text: str) -> str:
    lines = _lines(text)
    return lines[-1].strip() if lines else ""


def _indent_of_last_line(text: str) -> str:
    for line in reversed(text.splitlines()):
        if line.strip():
            return line[: len(line) - len(line.lstrip(" "))]
    return ""


def _next_indent(text: str) -> str:
    last_line = _last_meaningful_line(text).lower()
    indent = _indent_of_last_line(text)
    block_openers = (
        "for ",
        "for each",
        "while ",
        "if ",
        "else",
        "otherwise",
        "repeat ",
    )
    if any(last_line.startswith(prefix) for prefix in block_openers):
        return indent + "  "
    return indent


def _token_set(text: str) -> set[str]:
    return set(re.findall(r"[a-zA-Z_]{2,}", text.lower()))


def _problem_bucket(ctx: RequestContext) -> str:
    text = _normalize_text(f"{ctx.problem} {ctx.user_thought} {ctx.pseudocode}")
    rules = [
        ("two_sum", ["two sum", "target", "pair sum", "complement"]),
        ("parentheses", ["parentheses", "bracket", "balanced", "opening", "closing"]),
        ("binary_search", ["binary search", "sorted array", "middle", "mid"]),
        ("fibonacci", ["fibonacci"]),
        ("linked_list_reverse", ["reverse linked list", "linked list", "reverse list", "pointer"]),
        ("graph_shortest_path", ["shortest path", "minimum steps", "minimum edges", "unweighted graph"]),
        ("graph_traversal", ["graph traversal", "dfs", "bfs", "visit nodes", "graph"]),
        ("dynamic_programming", ["dynamic programming", "memo", "tabulation", "dp"]),
        ("sliding_window", ["window", "substring", "subarray", "sliding"]),
        ("prefix_sum", ["prefix sum", "running sum", "cumulative"]),
        ("merge_intervals", ["merge intervals", "interval"]),
        ("tree_traversal", ["tree traversal", "binary tree", "root", "left child", "right child"]),
    ]
    for bucket, keywords in rules:
        if any(keyword in text for keyword in keywords):
            return bucket
    return "generic"


def _contains_any(text: str, options: list[str]) -> bool:
    lowered = text.lower()
    return any(option in lowered for option in options)


def _detect_stage(ctx: RequestContext, bucket: str) -> str:
    pseudo = ctx.pseudocode.lower()
    thought = ctx.user_thought.lower()
    combined = f"{pseudo}\n{thought}"

    if not pseudo.strip():
        return "state_setup"

    if bucket == "two_sum":
        if not _contains_any(combined, ["seen", "map", "hash", "dictionary"]):
            return "state_setup"
        if not _contains_any(combined, ["for ", "for each", "iterate"]):
            return "iteration"
        if not _contains_any(combined, ["target -", "complement", "needed"]):
            return "compute_helper"
        if not _contains_any(combined, ["if complement", "if needed", "exists in seen", "lookup"]):
            return "decision_step"
        if not _contains_any(combined, ["store", "seen[number]", "add number to seen", "map[number]"]):
            return "state_update"
        return "return_step"

    if bucket == "parentheses":
        if not _contains_any(combined, ["stack"]):
            return "state_setup"
        if not _contains_any(combined, ["for each", "for symbol", "for char", "iterate"]):
            return "iteration"
        if not _contains_any(combined, ["push", "append opening"]):
            return "state_update"
        if not _contains_any(combined, ["pop", "top of stack", "matches"]):
            return "decision_step"
        return "return_step"

    if bucket == "binary_search":
        if not _contains_any(combined, ["left", "right"]):
            return "state_setup"
        if not _contains_any(combined, ["while left", "while low", "repeat while"]):
            return "iteration"
        if not _contains_any(combined, ["mid", "middle"]):
            return "compute_helper"
        if not _contains_any(combined, ["if value at mid", "if middle equals", "compare middle"]):
            return "decision_step"
        return "state_update"

    if bucket == "fibonacci":
        if not _contains_any(combined, ["if n <= 1", "if n is 0", "base case"]):
            return "base_case"
        if not _contains_any(combined, ["prev", "curr", "dp", "memo"]):
            return "state_setup"
        if not _contains_any(combined, ["for ", "repeat", "fib(n-1)", "fib(n - 1)"]):
            return "iteration"
        return "return_step"

    if bucket == "linked_list_reverse":
        if not _contains_any(combined, ["prev", "current"]):
            return "state_setup"
        if not _contains_any(combined, ["next", "next node", "temp"]):
            return "compute_helper"
        if not _contains_any(combined, ["current.next = prev", "point current to prev", "reverse link"]):
            return "state_update"
        return "return_step"

    if bucket in {"graph_shortest_path", "graph_traversal"}:
        if not _contains_any(combined, ["queue", "stack", "visited"]):
            return "state_setup"
        if not _contains_any(combined, ["start", "enqueue start", "push start"]):
            return "compute_helper"
        if not _contains_any(combined, ["while queue", "while stack", "repeat while"]):
            return "iteration"
        if not _contains_any(combined, ["for neighbor", "for each neighbor", "adjacent"]):
            return "decision_step"
        return "state_update"

    if bucket == "dynamic_programming":
        if not _contains_any(combined, ["memo", "dp", "table"]):
            return "state_setup"
        if not _contains_any(combined, ["base case", "if index", "if amount", "if n"]):
            return "base_case"
        if not _contains_any(combined, ["take", "skip", "transition", "dp[i]", "best of"]):
            return "decision_step"
        return "return_step"

    if bucket == "sliding_window":
        if not _contains_any(combined, ["left", "window"]):
            return "state_setup"
        if not _contains_any(combined, ["for right", "expand", "move right"]):
            return "iteration"
        if not _contains_any(combined, ["while invalid", "while count", "shrink", "move left"]):
            return "decision_step"
        return "return_step"

    if bucket == "prefix_sum":
        if not _contains_any(combined, ["prefix", "running sum"]):
            return "state_setup"
        if not _contains_any(combined, ["for each", "for number", "iterate"]):
            return "iteration"
        return "state_update"

    if bucket == "merge_intervals":
        if not _contains_any(combined, ["sort"]):
            return "state_setup"
        if not _contains_any(combined, ["merged", "result"]):
            return "compute_helper"
        if not _contains_any(combined, ["if current interval overlaps", "if overlap"]):
            return "decision_step"
        return "state_update"

    if bucket == "tree_traversal":
        if not _contains_any(combined, ["if node is null", "if root is null", "base case"]):
            return "base_case"
        if not _contains_any(combined, ["visit", "append root", "process root"]):
            return "decision_step"
        return "state_update"

    if "stuck" in thought or "confused" in thought or "don't know" in thought:
        if not _contains_any(combined, ["if ", "check ", "compare "]):
            return "decision_step"

    if not _contains_any(combined, ["for ", "while ", "repeat "]):
        return "iteration"
    if not _contains_any(combined, ["if ", "check ", "compare "]):
        return "decision_step"
    if not _contains_any(combined, ["return", "output"]):
        return "return_step"
    return "state_update"


def _score_example(ctx: RequestContext, bucket: str, stage: str, example: dict[str, Any]) -> float:
    score = 0.0
    if example.get("problem_type") == bucket:
        score += 5.0
    elif example.get("problem_type") == "generic":
        score += 1.0

    if example.get("stage") == stage:
        score += 4.0

    query_tokens = _token_set(f"{ctx.problem} {ctx.user_thought} {ctx.pseudocode}")
    example_tokens = _token_set(
        f"{example.get('problem', '')} {example.get('input_pseudocode', '')} {example.get('explanation', '')}"
    )
    overlap = len(query_tokens & example_tokens)
    score += min(overlap, 8) * 0.35

    return score


def _find_examples(ctx: RequestContext, bucket: str, stage: str, limit: int = 3) -> list[dict[str, Any]]:
    ranked: list[tuple[float, dict[str, Any]]] = []
    for example in _load_dataset():
        score = _score_example(ctx, bucket, stage, example)
        if score > 0:
            ranked.append((score, example))

    ranked.sort(key=lambda item: item[0], reverse=True)
    return [example for _, example in ranked[:limit]]


def _fallback_steps(bucket: str, stage: str) -> list[dict[str, str]]:
    steps: dict[tuple[str, str], list[dict[str, str]]] = {
        ("two_sum", "state_setup"): [
            {"line": "create a map called seen_values", "purpose": "store earlier numbers for fast lookup"},
            {"line": "start with seen_values as empty", "purpose": "prepare memory before iterating"},
        ],
        ("two_sum", "compute_helper"): [
            {"line": "set complement = target - current_number", "purpose": "compute what partner is needed"},
            {"line": "name the missing value before checking the map", "purpose": "make the next check clearer"},
        ],
        ("two_sum", "decision_step"): [
            {"line": "if complement exists in seen_values", "purpose": "check whether the answer is already available"},
            {"line": "if the needed partner was seen earlier", "purpose": "turn the idea into a direct test"},
        ],
        ("two_sum", "state_update"): [
            {"line": "store current_number with its index in seen_values", "purpose": "save information for later elements"},
            {"line": "add the current value after the check", "purpose": "avoid matching the number with itself too early"},
        ],
        ("parentheses", "state_setup"): [
            {"line": "create an empty stack", "purpose": "track unmatched opening symbols"},
            {"line": "prepare a map from closing bracket to opening bracket", "purpose": "support matching checks"},
        ],
        ("parentheses", "decision_step"): [
            {"line": "if stack is empty or top of stack does not match current closing bracket", "purpose": "reject invalid order immediately"},
            {"line": "otherwise pop the matching opening bracket", "purpose": "remove a resolved pair"},
        ],
        ("binary_search", "state_setup"): [
            {"line": "set left = 0 and right = last index", "purpose": "define the search space"},
            {"line": "keep two pointers for the active range", "purpose": "prepare for halving the range"},
        ],
        ("binary_search", "compute_helper"): [
            {"line": "set mid = floor((left + right) / 2)", "purpose": "inspect the middle element"},
            {"line": "choose the current middle position", "purpose": "compare against the target"},
        ],
        ("binary_search", "state_update"): [
            {"line": "if middle value is smaller than target then move left to mid + 1", "purpose": "discard the left half"},
            {"line": "otherwise move right to mid - 1", "purpose": "discard the right half"},
        ],
        ("fibonacci", "base_case"): [
            {"line": "if n is 0 or 1 then return n", "purpose": "stop the recurrence on smallest inputs"},
            {"line": "handle the smallest Fibonacci values first", "purpose": "avoid unnecessary work later"},
        ],
        ("linked_list_reverse", "state_setup"): [
            {"line": "set prev = null and current = head", "purpose": "prepare two moving pointers"},
            {"line": "begin with one pointer behind the list", "purpose": "make reversal possible"},
        ],
        ("linked_list_reverse", "compute_helper"): [
            {"line": "store next_node = current.next", "purpose": "avoid losing the rest of the list"},
            {"line": "save the next pointer before changing links", "purpose": "protect access to remaining nodes"},
        ],
        ("linked_list_reverse", "state_update"): [
            {"line": "point current.next to prev", "purpose": "reverse one link"},
            {"line": "move prev to current and current to next_node", "purpose": "advance both pointers"},
        ],
        ("graph_shortest_path", "state_setup"): [
            {"line": "create a queue and a visited set", "purpose": "prepare breadth-first search"},
            {"line": "store nodes to explore level by level", "purpose": "support shortest-step traversal"},
        ],
        ("graph_shortest_path", "decision_step"): [
            {"line": "for each neighbor of current node", "purpose": "expand the next frontier"},
            {"line": "if neighbor has not been visited then add it to queue", "purpose": "avoid repeated work"},
        ],
        ("dynamic_programming", "state_setup"): [
            {"line": "create a memo table for repeated states", "purpose": "reuse previous results"},
            {"line": "store answers by state before returning", "purpose": "avoid recomputation"},
        ],
        ("sliding_window", "decision_step"): [
            {"line": "while the window is invalid move left forward", "purpose": "restore the required condition"},
            {"line": "shrink the window until it satisfies the rule again", "purpose": "keep the window legal"},
        ],
        ("generic", "iteration"): [
            {"line": "for each item in the input", "purpose": "move through the data in a controlled way"},
            {"line": "repeat the next check for every element", "purpose": "turn the idea into a process"},
        ],
        ("generic", "decision_step"): [
            {"line": "if the current value satisfies the needed condition", "purpose": "make the next branch explicit"},
            {"line": "otherwise continue to the next candidate", "purpose": "separate good and bad cases"},
        ],
        ("generic", "return_step"): [
            {"line": "return the final answer", "purpose": "finish once the important state is ready"},
            {"line": "output the stored result", "purpose": "convert the built state into an answer"},
        ],
    }
    return steps.get((bucket, stage)) or steps.get(("generic", stage), [])


def _adapt_line(line: str, ctx: RequestContext) -> str:
    indent = _next_indent(ctx.pseudocode)
    return f"{indent}{line}".rstrip()


def _build_suggestions(ctx: RequestContext, bucket: str, stage: str) -> list[dict[str, str]]:
    examples = _find_examples(ctx, bucket, stage)
    suggestions: list[dict[str, str]] = []
    seen_lines: set[str] = set()

    for example in examples:
        for item in example.get("next_steps", []):
            line = _adapt_line(str(item.get("line", "")).strip(), ctx)
            purpose = str(item.get("purpose", "")).strip()
            if line and line not in seen_lines:
                suggestions.append({"line": line, "purpose": purpose})
                seen_lines.add(line)
            if len(suggestions) >= 4:
                return suggestions

    for item in _fallback_steps(bucket, stage):
        line = _adapt_line(item["line"], ctx)
        if line not in seen_lines:
            suggestions.append({"line": line, "purpose": item["purpose"]})
            seen_lines.add(line)
        if len(suggestions) >= 4:
            break

    return suggestions


def _build_strategy(bucket: str, stage: str) -> str:
    messages = {
        "state_setup": "The student likely needs one small setup step before the rest of the pseudocode can move forward.",
        "iteration": "The next bridge is probably the loop or traversal step that starts processing the input.",
        "compute_helper": "A helpful next line is one that names an intermediate value so the later decision becomes easy.",
        "decision_step": "The student seems close to the key check, so the next line should express the deciding condition.",
        "state_update": "The next bridge is probably an update to the running state after a check succeeds or fails.",
        "base_case": "The solution needs a stopping condition before recursive or repeated work becomes safe.",
        "return_step": "The core logic is close; the next line should convert that progress into the final answer.",
    }
    bucket_notes = {
        "two_sum": "For Two Sum style problems, the bridge usually connects the current number with stored earlier information.",
        "parentheses": "For bracket problems, order matters, so the bridge often involves stack behavior rather than counting alone.",
        "binary_search": "For binary search, each next line should help remove half of the remaining range.",
        "linked_list_reverse": "For linked-list reversal, good bridge lines protect pointers before changing them.",
        "graph_shortest_path": "For shortest-path style graph tasks, the bridge usually keeps the traversal level by level.",
        "dynamic_programming": "For DP, the next helpful line often stores or combines subproblem answers.",
        "generic": "The bridge should be a small, meaningful step rather than the full solution.",
    }
    return f"{messages.get(stage, messages['decision_step'])} {bucket_notes.get(bucket, bucket_notes['generic'])}"


def _build_focus_area(ctx: RequestContext, stage: str) -> str:
    last_line = _last_meaningful_line(ctx.pseudocode)
    if last_line:
        return (
            f"The pseudocode currently stops near `{last_line}`, so the next suggestion should extend that idea "
            f"without finishing the whole problem."
        )

    stage_hints = {
        "state_setup": "Start by preparing the one data structure or variable that the later logic depends on.",
        "iteration": "Start by saying how you will move through the input.",
        "compute_helper": "Start by naming the useful value that makes the next check easier.",
        "decision_step": "Start by writing the condition that separates the correct case from the wrong one.",
        "state_update": "Start by updating the tracked state after each step.",
        "base_case": "Start by handling the smallest case that should stop the process.",
        "return_step": "Start by turning the tracked state into the final answer.",
    }
    return stage_hints.get(stage, stage_hints["decision_step"])


def predict(payload: Any) -> dict[str, Any]:
    ctx = _parse_request(payload)
    bucket = _problem_bucket(ctx)
    stage = _detect_stage(ctx, bucket)
    matched_examples = _find_examples(ctx, bucket, stage)
    suggestions = _build_suggestions(ctx, bucket, stage)

    guidance = [
        "These suggestions are intentionally partial pseudocode steps. The student should choose, adapt, or reject them.",
        "Not every suggested line has to be perfectly correct. A useful bridge can still help the student discover the right path.",
    ]

    return {
        "prediction": "SUGGEST_NEXT_PSEUDOCODE_LINES",
        "problem_type": bucket,
        "language": ctx.language,
        "stage": stage,
        "focus_area": _build_focus_area(ctx, stage),
        "reasoning": _build_strategy(bucket, stage),
        "next_line_suggestions": [item["line"] for item in suggestions],
        "suggestion_details": suggestions,
        "guidance": guidance,
        "related_examples": [
            {
                "problem": example.get("problem", ""),
                "stage": example.get("stage", ""),
                "explanation": example.get("explanation", ""),
            }
            for example in matched_examples
        ],
    }
