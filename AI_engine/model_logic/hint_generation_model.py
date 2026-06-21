from __future__ import annotations

import re
from typing import Any


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def _problem_bucket(title: str, description: str, tags: list[str]) -> str:
    text = _normalize_text(f"{title} {description} {' '.join(tags)}")
    rules = [
        ("two_sum", ["two sum", "target", "pair sum", "complement"]),
        ("parentheses", ["parentheses", "bracket", "balanced", "opening", "closing"]),
        ("binary_search", ["binary search", "sorted array", "middle", "mid"]),
        ("fibonacci", ["fibonacci"]),
        ("linked_list_reverse", ["reverse linked list", "linked list", "reverse list", "pointer"]),
        ("graph_shortest_path", ["shortest path", "minimum steps", "minimum edges", "unweighted graph"]),
        ("graph_traversal", ["graph traversal", "dfs", "bfs", "visit nodes", "graph"]),
        ("dynamic_programming", ["dynamic programming", "memo", "tabulation", "dp", "coin change"]),
        ("sliding_window", ["window", "substring", "subarray", "sliding"]),
        ("prefix_sum", ["prefix sum", "running sum", "cumulative"]),
        ("merge_intervals", ["merge intervals", "interval"]),
        ("tree_traversal", ["tree traversal", "binary tree", "root", "left child", "right child"]),
    ]
    for bucket, keywords in rules:
        if any(keyword in text for keyword in keywords):
            return bucket
    return "generic"


def predict(payload: Any) -> list[dict[str, Any]]:
    """Generates 3 levels of progressive hints for any problem."""
    title = ""
    description = ""
    tags: list[str] = []

    if isinstance(payload, dict):
        title = str(payload.get("title", "")).strip()
        description = str(payload.get("description", "")).strip()
        raw_tags = payload.get("tags") or []
        if isinstance(raw_tags, list):
            tags = [str(t) for t in raw_tags]
        elif isinstance(raw_tags, str):
            tags = [raw_tags]
    else:
        title = str(payload or "").strip()

    bucket = _problem_bucket(title, description, tags)

    # Curated hints for known problem types
    hints_database: dict[str, list[str]] = {
        "two_sum": [
            "Think about how you would solve this manually. What information would you need to keep track of as you iterate through the list?",
            "Consider using a Hash Table (dictionary) to store the indices of values you've already seen. This can help you find complements in O(1) time.",
            "As you iterate, check if (target - current_number) exists in your Hash Table. If it does, you've found the matching pair!"
        ],
        "parentheses": [
            "We need to ensure brackets close in the correct order. How can we keep track of the most recently opened bracket that hasn't been closed yet?",
            "Use a Stack data structure. When you see an opening bracket, push it. When you see a closing bracket, verify if it matches the top of the stack.",
            "If the stack is empty when encountering a closing bracket, or if the popped bracket doesn't match the closing one, the string is invalid. At the end, the stack must be empty."
        ],
        "binary_search": [
            "The key property is that the input array is sorted. How can we use this to avoid checking every single element?",
            "Maintain two pointers, left and right. Find the middle element. Compare it to the target to discard half of the search range in each step.",
            "If target is greater than the middle element, set left to mid + 1. If smaller, set right to mid - 1. Repeat until left exceeds right."
        ],
        "fibonacci": [
            "The base cases are F(0) = 0 and F(1) = 1. The recursion is F(n) = F(n-1) + F(n-2). how can we prevent recalculating the same values?",
            "Use memoization (storing computed values in a dictionary/array) or tabulation (building from the bottom up iteratively).",
            "An iterative approach using just two variables (prev, curr) can solve this in O(N) time and O(1) space by shifting values forward."
        ],
        "linked_list_reverse": [
            "If we change a node's next pointer directly to point to its predecessor, we lose reference to the rest of the list. how can we prevent this?",
            "Use a temporary pointer to store the address of the next node before modifying the current node's next link.",
            "Maintain two pointers: prev (starts as null) and current (starts as head). In each step, save current.next, reverse current.next to prev, then advance both pointers."
        ],
        "graph_shortest_path": [
            "For finding the shortest path in an unweighted graph, depth-first search might go very deep down a suboptimal path. Which traversal style explores level-by-level?",
            "Breadth-First Search (BFS) is optimal for unweighted graphs because it visits nodes in order of their distance from the start.",
            "Use a Queue to hold nodes to visit and a Set to track visited nodes. Store the nodes alongside their distance from the start (node, distance)."
        ],
        "graph_traversal": [
            "To traverse a graph fully, we must keep track of where we have been to avoid infinite loops caused by cycles.",
            "Use a visited Set to store visited node identifiers. You can perform BFS using a Queue or DFS using recursion (call stack) or an explicit Stack.",
            "For each popped/visited node, iterate through its neighbors. If a neighbor is not visited, mark it as visited and add it to your queue/stack."
        ],
        "dynamic_programming": [
            "Identify the subproblems. How does the solution to the current state relate to the solutions of smaller, previously solved states?",
            "Determine the transition equation. For example, in Coin Change, the min coins for amount A is 1 + min(coins for A - coin) for all valid coins.",
            "Create a DP array or memoization table initialized with base cases (e.g., dp[0] = 0). Fill the table iteratively or recursively with memoization."
        ],
        "sliding_window": [
            "When asked to find a contiguous subarray or substring, nested loops take O(N^2). Can we expand and shrink a window dynamically instead?",
            "Use two pointers, left and right, to represent the window bounds. Expand the window by incrementing the right pointer.",
            "When the window becomes invalid (e.g. contains duplicates or violates constraints), increment the left pointer to shrink the window until it is valid again."
        ],
        "prefix_sum": [
            "If you need to query sum ranges repeatedly, doing a loop each time takes O(N) per query. Can we precompute cumulative sums?",
            "Create an array prefix_sum where prefix_sum[i] stores the sum of elements from index 0 to i-1.",
            "The sum of any range [L, R] can be computed in O(1) time using: prefix_sum[R + 1] - prefix_sum[L]."
        ],
        "merge_intervals": [
            "If intervals are in arbitrary order, checking overlaps requires comparing every interval with all others. How can we order them to make check local?",
            "Sort the intervals by their start times. This guarantees that any overlapping intervals will be adjacent in the sorted list.",
            "Iterate through the sorted intervals. If the current interval overlaps with the last merged interval, merge them by extending the end time."
        ],
        "tree_traversal": [
            "Tree structures are recursive. How can we define the traversal (inorder, preorder, postorder) recursively?",
            "For Inorder traversal, the sequence is: Traverse Left subtree, Visit Root node, Traverse Right subtree.",
            "Implement a recursive helper function. If the current node is null, return. Otherwise, call helper(node.left), record node.val, and call helper(node.right)."
        ],
    }

    if bucket in hints_database:
        selected = hints_database[bucket]
    else:
        # Dynamic Heuristic Hints for any generic/future problem
        # Extract keywords to sound smart
        keywords_in_title = [w for w in re.findall(r"\w+", title) if len(w) > 3]
        subject = keywords_in_title[0] if keywords_in_title else "input data"

        selected = [
            f"Start by defining a brute force approach for {title or 'this problem'}. Trace it manually on a small example to see where the bottleneck is.",
            f"Think about what data structure (like a Hash Table, Set, or Stack) or technique could eliminate redundant work on the {subject}.",
            "Analyze the constraints. If the input size is large (e.g., N >= 10^5), aim for an O(N) or O(N log N) solution. Avoid nested loops if possible."
        ]

    return [
        {"level": 1, "hint": selected[0], "unlocked": False},
        {"level": 2, "hint": selected[1], "unlocked": False},
        {"level": 3, "hint": selected[2], "unlocked": False},
    ]
