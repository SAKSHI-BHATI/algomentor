import streamlit as st
import numpy as np
import time
import re
import ast
import inspect
import sys
import textwrap
from collections import deque
from itertools import chain

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG & CSS  (identical look to app5)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(layout="wide", page_title="AlgoMentor — Algorithm Visualizer")
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* ── GLOBAL RESET & BASE ─────────────────────────────────── */
    html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif !important;
    }
    .main {
        background: linear-gradient(135deg, #e8f4fd 0%, #f0f8ff 50%, #dceefb 100%);
        color: #1a3a5c;
        min-height: 100vh;
    }
    .block-container { padding-top: 1.5rem !important; }

    /* ── HEADINGS ────────────────────────────────────────────── */
    h1 {
        background: linear-gradient(90deg, #1a6fbf, #2196f3, #0d9bd6);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-size: 2rem !important; font-weight: 700 !important;
        letter-spacing: -0.02em; margin-bottom: 0.2rem !important;
    }
    h2, h3 {
        color: #1a6fbf !important; font-weight: 600 !important;
        letter-spacing: -0.01em;
    }

    /* ── SIDEBAR ─────────────────────────────────────────────── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ddeeff 0%, #cce4f9 100%) !important;
        border-right: 1px solid rgba(30, 100, 190, 0.18) !important;
    }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stTextInput label,
    [data-testid="stSidebar"] .stNumberInput label,
    [data-testid="stSidebar"] .stRadio label,
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown li { color: #2a5a8a !important; font-size: 0.88rem; }
    [data-testid="stSidebar"] h2 { color: #1a6fbf !important; font-size: 1rem !important; margin-bottom: 1rem; }

    /* Sidebar selectbox & input fields */
    [data-testid="stSidebar"] .stSelectbox > div > div,
    [data-testid="stSidebar"] .stTextInput > div > div > input,
    [data-testid="stSidebar"] .stNumberInput > div > div > input {
        background-color: #f0f8ff !important;
        border: 1px solid rgba(30, 100, 190, 0.3) !important;
        color: #1a3a5c !important;
        border-radius: 8px !important;
    }
    [data-testid="stSidebar"] .stSelectbox > div > div:hover,
    [data-testid="stSidebar"] .stTextInput > div > div > input:focus,
    [data-testid="stSidebar"] .stNumberInput > div > div > input:focus {
        border-color: rgba(30, 100, 190, 0.65) !important;
        box-shadow: 0 0 0 2px rgba(30, 100, 190, 0.12) !important;
    }

    /* ── BUTTONS ─────────────────────────────────────────────── */
    .stButton > button {
        background: linear-gradient(135deg, #1a7de0 0%, #0d9bd6 100%) !important;
        color: #ffffff !important; border: none !important;
        border-radius: 10px !important; padding: 10px 22px !important;
        font-weight: 600 !important; font-size: 0.9rem !important;
        letter-spacing: 0.02em !important;
        transition: all 0.25s ease !important;
        box-shadow: 0 4px 16px rgba(26, 125, 224, 0.3) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(26, 125, 224, 0.45) !important;
        background: linear-gradient(135deg, #2289ee 0%, #18adea 100%) !important;
    }
    .stButton > button:active { transform: translateY(0) !important; }

    /* ── ARRAY VISUALIZATION ─────────────────────────────────── */
    .array-container {
        display: flex; flex-wrap: wrap; gap: 10px; padding: 18px 20px;
        border: 1px solid rgba(26, 111, 191, 0.2);
        border-radius: 16px;
        background: linear-gradient(135deg, rgba(255,255,255,0.92), rgba(240,248,255,0.95));
        box-shadow: 0 4px 24px rgba(26, 111, 191, 0.1), inset 0 1px 0 rgba(255,255,255,0.8);
    }
    .array-element {
        padding: 10px 14px; border-radius: 10px; color: #1a3a5c;
        min-width: 44px; text-align: center; font-weight: 600;
        font-size: 1.05rem;
        background: rgba(255, 255, 255, 0.85);
        border: 1px solid rgba(26, 111, 191, 0.2);
        transition: all 0.25s ease;
        font-family: 'JetBrains Mono', monospace;
        box-shadow: 0 2px 6px rgba(26, 111, 191, 0.08);
    }
    .compare-element {
        background: linear-gradient(135deg, #f0b429, #f0820f) !important;
        color: #fff !important; font-weight: 700 !important;
        border-color: #f0b429 !important;
        box-shadow: 0 0 16px rgba(240, 180, 41, 0.4) !important;
        transform: scale(1.12) !important;
    }
    .swap-element {
        background: linear-gradient(135deg, #f25c78, #d63060) !important;
        color: #fff !important; font-weight: 700 !important;
        border-color: #f25c78 !important;
        box-shadow: 0 0 20px rgba(242, 92, 120, 0.4) !important;
        transform: scale(1.18) !important;
    }
    .sorted-element {
        background: linear-gradient(135deg, #10c97a, #0fa86a) !important;
        color: #fff !important; font-weight: 700 !important;
        border-color: #10c97a !important;
        box-shadow: 0 0 14px rgba(16, 201, 122, 0.3) !important;
        transform: scale(1.08) !important;
    }
    .active-element {
        background: linear-gradient(135deg, #1a7de0, #2196f3) !important;
        color: #fff !important;
        border-color: #2196f3 !important;
        box-shadow: 0 0 18px rgba(33, 150, 243, 0.4) !important;
    }
    .found-element {
        background: linear-gradient(135deg, #20e08a, #0fc97a) !important;
        color: #fff !important; font-weight: 700 !important;
        border-color: #20e08a !important;
        box-shadow: 0 0 22px rgba(32, 224, 138, 0.45) !important;
        transform: scale(1.2) !important;
    }

    /* ── INFO & ERROR BOXES ──────────────────────────────────── */
    .info-box {
        border-left: 4px solid #1a7de0; border-radius: 8px; padding: 12px 16px;
        background: linear-gradient(135deg, rgba(255,255,255,0.97), rgba(235,247,255,0.95));
        margin-top: 12px; color: #1a4a7a;
        font-size: 0.9rem; letter-spacing: 0.01em;
        border: 1px solid rgba(26, 125, 224, 0.2);
        border-left: 4px solid #1a7de0;
        box-shadow: 0 2px 12px rgba(26, 111, 191, 0.1);
    }
    .error-box {
        border-left: 4px solid #f25c78; border-radius: 8px; padding: 12px 16px;
        background: rgba(255, 240, 244, 0.95); margin-top: 12px;
        color: #c0334d; font-family: 'JetBrains Mono', monospace; font-size: 0.82rem;
        border: 1px solid rgba(242, 92, 120, 0.3);
    }

    /* ── SPLIT PANELS ────────────────────────────────────────── */
    .split-panel {
        display: grid; grid-template-columns: 1fr 1fr; gap: 18px; margin-top: 14px;
    }
    .panel-box {
        background: linear-gradient(135deg, rgba(255,255,255,0.97), rgba(240,248,255,0.95));
        border: 1px solid rgba(26, 111, 191, 0.18);
        border-radius: 16px; padding: 16px 18px; min-height: 320px;
        box-shadow: 0 4px 20px rgba(26, 111, 191, 0.1), inset 0 1px 0 rgba(255,255,255,0.9);
        backdrop-filter: blur(4px);
    }
    .panel-title {
        color: #1a6fbf; font-size: 0.78rem; font-weight: 700;
        letter-spacing: 0.12em; text-transform: uppercase;
        margin-bottom: 12px;
        padding-bottom: 8px;
        border-bottom: 1px solid rgba(26, 111, 191, 0.15);
        display: flex; align-items: center; gap: 8px;
    }

    /* ── CODE BLOCK ──────────────────────────────────────────── */
    .code-block {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem; line-height: 1.8; white-space: pre;
    }
    .code-line {
        display: block; padding: 2px 8px; border-radius: 5px;
        color: #5a7a9a; transition: all 0.2s;
    }
    .code-line.active-line {
        background: linear-gradient(90deg, rgba(33,150,243,0.15), rgba(33,150,243,0.04));
        color: #0d4a8a;
        border-left: 3px solid #1a7de0; padding-left: 5px;
        font-weight: 600;
        box-shadow: inset 0 0 0 1px rgba(33,150,243,0.1);
    }

    /* ── STEP TABLE ──────────────────────────────────────────── */
    .step-table { width: 100%; border-collapse: collapse; font-size: 0.82rem; margin-top: 6px; }
    .step-table th {
        background: rgba(26, 111, 191, 0.1); color: #1a6fbf;
        padding: 7px 12px; text-align: left; font-weight: 700;
        letter-spacing: 0.05em; text-transform: uppercase; font-size: 0.72rem;
        border-bottom: 1px solid rgba(26, 111, 191, 0.18);
    }
    .step-table td { padding: 6px 12px; color: #2a5a8a; border-bottom: 1px solid rgba(26, 111, 191, 0.08); }
    .step-table tr:last-child td {
        background: rgba(16, 201, 122, 0.07); color: #0a8a56; font-weight: 600;
    }
    .step-table tr:hover td { background: rgba(26, 111, 191, 0.05); }
    .step-count-badge {
        display: inline-block;
        background: linear-gradient(135deg, rgba(26,125,224,0.15), rgba(13,155,214,0.12));
        color: #1a6fbf; border-radius: 20px; padding: 2px 10px;
        font-size: 0.72rem; font-weight: 700;
        margin-left: 8px; vertical-align: middle;
        border: 1px solid rgba(26, 111, 191, 0.25);
    }

    /* ── POINTER LABELS ──────────────────────────────────────── */
    .array-col { display: flex; flex-direction: column; align-items: center; gap: 4px; }
    .pointer-label {
        font-size: 0.72rem; font-weight: 700; font-family: 'JetBrains Mono', monospace;
        height: 18px; line-height: 18px;
    }
    .pointer-i    { color: #1a7de0; }
    .pointer-j    { color: #f25c78; }
    .pointer-ij   { color: #f0b429; }
    .pointer-none { visibility: hidden; }

    /* ── GRAPH CONTAINER ─────────────────────────────────────── */
    .graph-container {
        background: linear-gradient(135deg, rgba(255,255,255,0.97), rgba(235,247,255,0.95));
        border: 1px solid rgba(26, 111, 191, 0.2);
        border-radius: 16px; padding: 12px;
        box-shadow: 0 4px 24px rgba(26, 111, 191, 0.12);
    }

    /* ── HINT BOX ────────────────────────────────────────────── */
    .hint-box {
        border: 1px solid rgba(26, 111, 191, 0.22); border-radius: 10px;
        padding: 12px 16px;
        background: linear-gradient(135deg, rgba(235,247,255,0.97), rgba(220,240,255,0.92));
        font-size: 0.82rem; color: #2a5a8a;
        font-family: 'JetBrains Mono', monospace; margin-bottom: 10px;
    }
    .hint-box b { color: #1a6fbf; }

    /* ── SCROLLBAR ───────────────────────────────────────────── */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: rgba(200, 225, 245, 0.5); border-radius: 3px; }
    ::-webkit-scrollbar-thumb { background: rgba(26, 111, 191, 0.3); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(26, 111, 191, 0.55); }

    /* ── STREAMLIT OVERRIDES ─────────────────────────────────── */
    .stTextArea textarea {
        background: rgba(245, 251, 255, 0.97) !important;
        border: 1px solid rgba(26, 111, 191, 0.22) !important;
        color: #1a3a5c !important; border-radius: 10px !important;
        font-family: 'JetBrains Mono', monospace !important;
    }
    .stTextArea textarea:focus {
        border-color: rgba(26, 111, 191, 0.55) !important;
        box-shadow: 0 0 0 3px rgba(26, 111, 191, 0.1) !important;
    }
    div[data-testid="stMarkdownContainer"] p { color: #2a5a8a; }

    /* ── FULL PAGE BACKGROUND FIX ────────────────────────────── */
    .stApp { background: #e8f4fd !important; }
    [data-testid="stAppViewContainer"] { background: #e8f4fd !important; }
    [data-testid="stHeader"] { background: transparent !important; }
    section[data-testid="stSidebar"] > div { background: #ddeeff !important; }

    /* ── PULSE ANIMATION ─────────────────────────────────────── */
    @keyframes pulse {
        0%, 100% { box-shadow: 0 0 6px rgba(26,125,224,0.5); opacity: 1; }
        50% { box-shadow: 0 0 16px rgba(26,125,224,0.85); opacity: 0.7; }
    }

    /* ── ALGO TAG PILLS ──────────────────────────────────────── */
    .algo-tag {
        display: inline-block; padding: 3px 10px; border-radius: 20px;
        font-size: 0.72rem; font-weight: 700; letter-spacing: 0.06em;
        text-transform: uppercase; margin-right: 6px;
        border: 1px solid rgba(26, 111, 191, 0.28);
        background: rgba(26, 125, 224, 0.08); color: #1a6fbf;
    }

    /* ── STAT STRIP ──────────────────────────────────────────── */
    .stat-strip {
        display: flex; gap: 12px; margin-bottom: 16px;
    }
    .stat-card {
        flex: 1; padding: 12px 16px; border-radius: 12px;
        background: linear-gradient(135deg, rgba(255,255,255,0.97), rgba(235,247,255,0.95));
        border: 1px solid rgba(26, 111, 191, 0.15);
        text-align: center;
        box-shadow: 0 2px 10px rgba(26, 111, 191, 0.08);
    }
    .stat-val { font-size: 1.4rem; font-weight: 700; color: #1a7de0; font-family: 'JetBrains Mono', monospace; }
    .stat-lbl { font-size: 0.68rem; color: #5a8ab0; text-transform: uppercase; letter-spacing: 0.1em; font-weight: 600; margin-top: 2px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# ALGO CODE DEFINITIONS  (for the "Your Algorithm" panel)
# ─────────────────────────────────────────────────────────────────────────────
ALGO_CODE = {
    "Bubble Sort": [
        ("def bubble_sort(arr):", None),
        ("    n = len(arr)", None),
        ("    for i in range(n):", "outer"),
        ("        swapped = False", "outer"),
        ("        for j in range(0, n-i-1):", "compare"),
        ("            if arr[j] > arr[j+1]:", "compare"),
        ("                swap(arr, j, j+1)", "swap"),
        ("                swapped = True", "swap"),
        ("        if not swapped: break", None),
        ("    return arr  # Sorted!", "sorted"),
    ],
    "Selection Sort": [
        ("def selection_sort(arr):", None),
        ("    n = len(arr)", None),
        ("    for i in range(n):", "outer"),
        ("        min_idx = i", "outer"),
        ("        for j in range(i+1, n):", "compare"),
        ("            if arr[j] < arr[min_idx]:", "compare"),
        ("                min_idx = j", "new min"),
        ("        swap(arr, i, min_idx)", "placed"),
        ("    return arr  # Sorted!", "complete"),
    ],
    "Insertion Sort": [
        ("def insertion_sort(arr):", None),
        ("    for i in range(1, len(arr)):", "picking"),
        ("        key = arr[i]", "picking"),
        ("        j = i - 1", "picking"),
        ("        while j >= 0 and arr[j] > key:", "shifting"),
        ("            arr[j+1] = arr[j]", "shifting"),
        ("            j -= 1", "shifting"),
        ("        arr[j+1] = key", "inserted"),
        ("    return arr  # Sorted!", "complete"),
    ],
    "Linear Search": [
        ("def linear_search(arr, target):", None),
        ("    for i, val in enumerate(arr):", "checking"),
        ("        if val == target:", "checking"),
        ("            return i  # Found!", "found"),
        ("    return -1  # Not found", "not found"),
    ],
    "Binary Search": [
        ("def binary_search(arr, target):", None),
        ("    low, high = 0, len(arr)-1", None),
        ("    while low <= high:", "range"),
        ("        mid = (low+high) // 2", "range"),
        ("        if arr[mid] == target:", "range"),
        ("            return mid  # Found!", "found"),
        ("        elif arr[mid] < target:", "range"),
        ("            low = mid + 1", "range"),
        ("        else:", "range"),
        ("            high = mid - 1", "range"),
        ("    return -1  # Not found", "not found"),
    ],
    "Two Sum": [
        ("def two_sum(nums, target):", None),
        ("    hashmap = {}", "searching"),
        ("    for i, num in enumerate(nums):", "current"),
        ("        complement = target - num", "current"),
        ("        if complement in hashmap:", "current"),
        ("            return [hashmap[complement], i]", "found"),
        ("        hashmap[num] = i", "current"),
        ("    return []  # No solution", "no solution"),
    ],
    "Valid Parentheses": [
        ("def is_valid(s):", None),
        ("    stack = []", "processing"),
        ("    pairs = {')':'(', ']':'[', '}':'{'}", "processing"),
        ("    for ch in s:", "processing"),
        ("        if ch in '([{':", "processing"),
        ("            stack.append(ch)", "processing"),
        ("        elif stack[-1] != pairs[ch]:", "mismatch"),
        ("            return False", "invalid"),
        ("        else: stack.pop()", "processing"),
        ("    return not stack", "valid"),
    ],
    "Fibonacci DP": [
        ("def fibonacci(n):", None),
        ("    dp = [0] * (n+1)", "initialized"),
        ("    dp[1] = 1", "initialized"),
        ("    for i in range(2, n+1):", "dp["),
        ("        dp[i] = dp[i-1] + dp[i-2]", "dp["),
        ("    return dp[n]", "fibonacci"),
    ],
    "Reverse List": [
        ("def reverse_list(arr):", None),
        ("    prev = []", "starting"),
        ("    curr = list(arr)", "starting"),
        ("    while curr:", "moving"),
        ("        node = curr.pop(0)", "moving"),
        ("        prev = [node] + prev", "moving"),
        ("    return prev  # Reversed!", "reversal complete"),
    ],
    "BFS": [
        ("def bfs(graph, start):", None),
        ("    visited = set()", "starting bfs"),
        ("    queue = deque([start])", "starting bfs"),
        ("    visited.add(start)", "starting bfs"),
        ("    order = []", "starting bfs"),
        ("    while queue:", "visiting"),
        ("        node = queue.popleft()", "visiting"),
        ("        order.append(node)", "visiting"),
        ("        for nbr in graph[node]:", "neighbour"),
        ("            if nbr not in visited:", "neighbour"),
        ("                visited.add(nbr)", "neighbour"),
        ("                queue.append(nbr)", "neighbour"),
        ("    return order  # BFS Complete!", "bfs complete"),
    ],
    "DFS": [
        ("def dfs(graph, start):", None),
        ("    visited = set()", "starting dfs"),
        ("    stack = [start]", "starting dfs"),
        ("    order = []", "starting dfs"),
        ("    while stack:", "visiting"),
        ("        node = stack.pop()", "visiting"),
        ("        if node not in visited:", "visiting"),
        ("            visited.add(node)", "visiting"),
        ("            order.append(node)", "visiting"),
        ("            for nbr in reversed(graph[node]):", "neighbour"),
        ("                if nbr not in visited:", "neighbour"),
        ("                    stack.append(nbr)", "neighbour"),
        ("    return order  # DFS Complete!", "dfs complete"),
    ],
}


def get_active_lines(algo, message):
    msg = message.lower()
    code_lines = ALGO_CODE.get(algo, [])
    active = []
    for idx, (_, tag) in enumerate(code_lines):
        if tag and tag.lower() in msg:
            active.append(idx)
    if not active and any(k in msg for k in ("sorted","complete","found","valid","fibonacci","reversal","bfs complete","dfs complete")):
        active = [len(code_lines) - 1]
    return active


def render_code_panel(algo, active_lines, custom_lines=None):
    """Renders the 'Your Algorithm' panel. Uses custom_lines if provided."""
    if custom_lines is not None:
        lines = [(l, None) for l in custom_lines]
    else:
        lines = ALGO_CODE.get(algo, [])
    lines_html = ""
    for idx, (line, _) in enumerate(lines):
        cls = "code-line active-line" if idx in active_lines else "code-line"
        escaped = line.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
        lines_html += f"<span class='{cls}'>{escaped}</span>"
    return f"""<div class='panel-box'>
        <div class='panel-title'>📄 Your Algorithm</div>
        <div class='code-block'>{lines_html}</div>
    </div>"""


def render_execution_panel(steps_log):
    rows = ""
    for step_num, msg, arr_snapshot in steps_log:
        arr_str = str(arr_snapshot)[:40] + ("…" if len(str(arr_snapshot)) > 40 else "")
        rows += f"<tr><td>Step {step_num}</td><td>{msg}</td><td style='font-family:monospace;font-size:0.78rem'>{arr_str}</td></tr>"
    return f"""<div class='panel-box'>
        <div class='panel-title'>⚡ Step-by-Step Execution <span class='step-count-badge'>{len(steps_log)} steps</span></div>
        <div style='overflow-y:auto;max-height:300px;'>
        <table class='step-table'>
            <thead><tr><th>#</th><th>Action</th><th>State</th></tr></thead>
            <tbody>{rows}</tbody>
        </table></div>
    </div>"""


# ─────────────────────────────────────────────────────────────────────────────
# GRAPH HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def parse_graph_input(text):
    """
    Parse adjacency list from text like:
        0: 1 2
        1: 0 3 4
    Returns dict {node: [neighbours]} or raises ValueError.
    """
    graph = {}
    for line in text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        if ":" not in line:
            raise ValueError(f"Missing ':' in line: '{line}'")
        node_part, nbrs_part = line.split(":", 1)
        node = int(node_part.strip())
        nbrs = [int(x) for x in nbrs_part.split() if x.strip()]
        graph[node] = nbrs
    return graph


def compute_node_positions(graph):
    """
    Auto-layout nodes in a simple circular / layered arrangement.
    BFS from node 0 (or first node) to assign layers, then spread within layer.
    """
    if not graph:
        return {}
    nodes = list(graph.keys())
    root = nodes[0]

    # BFS to find layers
    layers = {}
    visited = {root: 0}
    q = deque([root])
    while q:
        n = q.popleft()
        layer = visited[n]
        layers.setdefault(layer, []).append(n)
        for nb in graph.get(n, []):
            if nb not in visited:
                visited[nb] = layer + 1
                q.append(nb)
    # nodes not reachable
    layer_idx = max(visited.values()) + 1 if visited else 0
    for n in nodes:
        if n not in visited:
            layers.setdefault(layer_idx, []).append(n)
            layer_idx += 1

    W, H = 700, 340
    pos = {}
    num_layers = max(layers.keys()) + 1
    y_step = H / (num_layers + 1)
    for layer, layer_nodes in layers.items():
        y = int(y_step * (layer + 1))
        x_step = W / (len(layer_nodes) + 1)
        for i, n in enumerate(layer_nodes):
            x = int(x_step * (i + 1))
            pos[n] = (x, y)
    return pos


DEFAULT_GRAPH_TEXT = "0: 1 2\n1: 0 3 4\n2: 0 5 6\n3: 1\n4: 1\n5: 2\n6: 2"


def parse_int_list(text):
    values = [chunk.strip() for chunk in re.split(r"[,\s]+", text.strip()) if chunk.strip()]
    if not values:
        return []
    return [int(value) for value in values]


def parse_context_literal(text):
    raw = text.strip()
    if not raw:
        return {}
    try:
        return ast.literal_eval(raw)
    except Exception as exc:
        raise ValueError(f"Context must be a valid Python literal / JSON-like value: {exc}") from exc


def render_graph_svg(graph, node_pos, visited_set, current_node, queue_or_stack):
    edges = [(u, v) for u in graph for v in graph[u] if u < v]
    lines = []
    lines.append("<svg viewBox='0 0 700 340' xmlns='http://www.w3.org/2000/svg' style='width:100%;height:auto;'>")
    lines.append("<defs><linearGradient id='bgGrad' x1='0' y1='0' x2='1' y2='1'><stop offset='0%' stop-color='#0b1028'/><stop offset='100%' stop-color='#101637'/></linearGradient></defs>")
    lines.append("<rect width='700' height='340' fill='url(#bgGrad)' rx='14'/>")
    for u, v in edges:
        if u in node_pos and v in node_pos:
            x1,y1 = node_pos[u]; x2,y2 = node_pos[v]
            lines.append(f"<line x1='{x1}' y1='{y1}' x2='{x2}' y2='{y2}' stroke='rgba(108,143,255,0.2)' stroke-width='2'/>")
    for node, (cx, cy) in node_pos.items():
        if node == current_node:
            fill,stroke,tc = "#f0b429","#f0d070","#0a0e1a"
        elif node in visited_set:
            fill,stroke,tc = "#10c97a","#30e09a","#0a0e1a"
        elif node in queue_or_stack:
            fill,stroke,tc = "#3d6ef5","#6c8fff","#ffffff"
        else:
            fill,stroke,tc = "rgba(255,255,255,0.04)","rgba(108,143,255,0.3)","#7a9aff"
        lines.append(f"<circle cx='{cx}' cy='{cy}' r='22' fill='{fill}' stroke='{stroke}' stroke-width='2'/>")
        lines.append(f"<text x='{cx}' y='{cy+5}' text-anchor='middle' font-size='13' font-weight='700' font-family='JetBrains Mono,monospace' fill='{tc}'>{node}</text>")
    legend_items = [("#f0b429","#0a0e1a","Current"),("#3d6ef5","#ffffff","In Queue/Stack"),("#10c97a","#0a0e1a","Visited"),("rgba(255,255,255,0.04)","#7a9aff","Unvisited")]
    lx = 14
    for fill,tc,label in legend_items:
        lines.append(f"<circle cx='{lx+9}' cy='320' r='8' fill='{fill}' stroke='#30363d' stroke-width='1.5'/>")
        lines.append(f"<text x='{lx+22}' y='325' font-size='11' font-family='sans-serif' fill='#8b949e'>{label}</text>")
        lx += 118
    lines.append("</svg>")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# ALGORITHM GENERATORS
# ─────────────────────────────────────────────────────────────────────────────
def swap(arr, i, j):
    arr[i], arr[j] = arr[j], arr[i]

def bubble_sort_visualizer(arr):
    n = len(arr)
    yield list(arr), -1, -1, "Starting Bubble Sort", False
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            yield list(arr), j, j+1, f"Comparing {arr[j]} and {arr[j+1]}", False
            if arr[j] > arr[j+1]:
                swap(arr, j, j+1); swapped = True
                yield list(arr), j, j+1, "Swapping elements", True
        if not swapped: break
    yield list(arr), -1, -1, "Array Sorted!", False

def selection_sort_visualizer(arr):
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i+1, n):
            yield list(arr), min_idx, j, f"Comparing min with {arr[j]}", False
            if arr[j] < arr[min_idx]:
                min_idx = j
                yield list(arr), min_idx, -1, f"New minimum: {arr[min_idx]}", False
        swap(arr, i, min_idx)
        yield list(arr), i, -1, f"Placed {arr[i]} at index {i}", True
    yield list(arr), -1, -1, "Sort Complete", False

def insertion_sort_visualizer(arr):
    for i in range(1, len(arr)):
        key = arr[i]; j = i - 1
        yield list(arr), i, j, f"Picking key: {key}", False
        while j >= 0 and arr[j] > key:
            arr[j+1] = arr[j]; j -= 1
            yield list(arr), j+1, -1, "Shifting element right", True
        arr[j+1] = key
        yield list(arr), j+1, -1, f"Inserted {key}", False
    yield list(arr), -1, -1, "Sort Complete", False

def linear_search_visualizer(arr, target):
    for i, val in enumerate(arr):
        yield list(arr), i, -1, f"Checking index {i}: {val}", False
        if val == target:
            yield list(arr), i, -1, f"Found {target}!", True; return
    yield list(arr), -1, -1, "Target not found", False

def binary_search_visualizer(arr, target):
    low, high = 0, len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        yield list(arr), mid, -1, f"Range: [{low}, {high}], Mid: {arr[mid]}", False
        if arr[mid] == target:
            yield list(arr), mid, -1, f"Found {target} at index {mid}!", True; return
        elif arr[mid] < target: low = mid + 1
        else: high = mid - 1
    yield list(arr), -1, -1, "Target not found", False

def two_sum_visualizer(nums, target):
    hashmap = {}
    yield list(nums), -1, -1, f"Searching for two numbers that sum to {target}", False
    for i, num in enumerate(nums):
        complement = target - num
        yield list(nums), i, -1, f"Current: {num}. Need complement: {complement}", False
        if complement in hashmap:
            yield list(nums), i, hashmap[complement], f"Found! {num} + {complement} = {target}", True; return
        hashmap[num] = i
    yield list(nums), -1, -1, "No solution found", False

def valid_parentheses_visualizer(s):
    stack = []; pairs = {')':'(', ']':'[', '}':'{'}; chars = list(s)
    for i, ch in enumerate(chars):
        yield stack + ["|"] + chars[i:], i, -1, f"Processing: {ch}", False
        if ch in "([{":
            stack.append(ch)
        else:
            if not stack or stack[-1] != pairs[ch]:
                yield stack + ["|"] + chars[i:], i, -1, "Mismatch! Invalid.", True; return
            stack.pop()
    yield stack, -1, -1, "Stack empty! Valid." if not stack else "Stack not empty! Invalid.", True

def fibonacci_dp_visualizer(n):
    dp = [0] * (n + 1)
    if n >= 1: dp[1] = 1
    yield dp, -1, -1, "Initialized DP table", False
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
        yield dp, i, -1, f"dp[{i}] = dp[{i-1}] + dp[{i-2}] = {dp[i]}", False
    yield dp, -1, -1, f"Fibonacci({n}) is {dp[n]}", True

def reverse_linked_list_visualizer(arr):
    prev = []; curr = list(arr)
    yield curr, -1, -1, "Starting reversal", False
    while curr:
        node = curr.pop(0); prev = [node] + prev
        yield prev + ["→"] + curr, -1, -1, f"Moving {node} to front", False
    yield prev, -1, -1, "Reversal complete", True

def bfs_visualizer(graph, start=0):
    visited = set(); queue = deque([start]); visited.add(start); order = []
    yield order, start, -1, f"Starting BFS from node {start}. Queue: {list(queue)}", False
    while queue:
        node = queue.popleft(); order.append(node)
        yield list(order), node, -1, f"Visiting node {node}. Visited order: {order}", True
        neighbours_added = []
        for nbr in graph.get(node, []):
            if nbr not in visited:
                visited.add(nbr); queue.append(nbr); neighbours_added.append(nbr)
        if neighbours_added:
            yield list(order), node, -1, f"Neighbour(s) {neighbours_added} added to queue. Queue: {list(queue)}", False
    yield list(order), -1, -1, f"BFS Complete! Traversal order: {order}", False

def dfs_visualizer(graph, start=0):
    visited = set(); stack = [start]; order = []
    yield order, start, -1, f"Starting DFS from node {start}. Stack: {stack}", False
    while stack:
        node = stack.pop()
        if node in visited:
            yield list(order), node, -1, f"Node {node} already visited, skipping.", False; continue
        visited.add(node); order.append(node)
        yield list(order), node, -1, f"Visiting node {node}. Visited order: {order}", True
        neighbours_added = []
        for nbr in reversed(graph.get(node, [])):
            if nbr not in visited:
                stack.append(nbr); neighbours_added.append(nbr)
        if neighbours_added:
            yield list(order), node, -1, f"Neighbour(s) {neighbours_added} pushed to stack. Stack: {stack}", False
    yield list(order), -1, -1, f"DFS Complete! Traversal order: {order}", False


# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM ALGORITHM RUNNER
# Executes user code and collects yield steps via a wrapper generator
# ─────────────────────────────────────────────────────────────────────────────
CUSTOM_TEMPLATE = '''\
# Write your algorithm as a generator function called `my_algorithm`.
# Use `yield` to emit each step as:
#   yield state_list, highlight_idx1, highlight_idx2, "message", is_swap_action
#
# Parameters available: arr (list of ints), target (int), n (int = len(arr))
#
# Example — linear search:
def my_algorithm(arr, target, n):
    for i, val in enumerate(arr):
        yield list(arr), i, -1, f"Checking index {i}: {val}", False
        if val == target:
            yield list(arr), i, -1, f"Found {target}!", True
            return
    yield list(arr), -1, -1, "Not found", False
'''

def run_custom_algorithm(user_code, arr, target):
    """
    Compile and run user-defined generator `my_algorithm(arr, target, n)`.
    Returns (generator, error_string).
    """
    namespace = {"deque": deque, "arr": list(arr), "target": target, "n": len(arr)}
    try:
        exec(compile(user_code, "<custom>", "exec"), namespace)
    except SyntaxError as e:
        return None, f"SyntaxError on line {e.lineno}: {e.msg}"
    except Exception as e:
        return None, f"Error during compile: {e}"
    if "my_algorithm" not in namespace:
        return None, "No function named `my_algorithm` found. Please define it."
    try:
        gen = namespace["my_algorithm"](list(arr), target, len(arr))
        return gen, None
    except Exception as e:
        return None, f"Error calling my_algorithm: {e}"


# ─────────────────────────────────────────────────────────────────────────────
# RENDERERS
# ─────────────────────────────────────────────────────────────────────────────
def render_array_html(curr_arr, idx1, idx2, message, is_action):
    html = "<div class='array-container'>"
    is_terminal = any(k in message for k in ("Sorted","Complete","Found","Valid","Fibonacci","Reversal","Complete!"))
    for i, val in enumerate(curr_arr):
        css = "array-element"
        if is_terminal:
            css += " sorted-element"
        elif i == idx1 or i == idx2:
            css += " swap-element" if is_action else " compare-element"
        if not is_terminal and idx1 != -1 and idx2 != -1 and i == idx1 and i == idx2:
            plabel = "<span class='pointer-label pointer-ij'>i=j</span>"
        elif not is_terminal and idx1 != -1 and i == idx1:
            plabel = "<span class='pointer-label pointer-i'>i</span>"
        elif not is_terminal and idx2 != -1 and i == idx2:
            plabel = "<span class='pointer-label pointer-j'>j</span>"
        else:
            plabel = "<span class='pointer-label pointer-none'>·</span>"
        html += f"<div class='array-col'><div class='{css}'>{val}</div>{plabel}</div>"
    html += "</div>"
    return html


def run_standard_render(gen, algo, custom_lines=None):
    stat_area    = st.empty()
    display_area = st.empty()
    log_area     = st.empty()
    st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)
    panels_area  = st.empty()
    steps_log    = []
    step_num     = 0
    for step in gen:
        curr_arr, idx1, idx2, message, is_action = step
        step_num += 1
        steps_log.append((step_num, message, curr_arr))
        # stat strip
        is_done = any(k in message for k in ("Sorted","Complete","Found","Valid","Fibonacci","Reversal","Complete!","not found"))
        status_color = "#10c97a" if is_done else "#3d5af1"
        status_label = "&#9989; Done" if is_done else "&#9654; Running"
        stat_area.markdown(f"""
<div style='display:flex;gap:10px;margin-bottom:12px;'>
  <div style='flex:1;padding:10px 14px;background:rgba(13,18,48,0.9);border:1px solid rgba(108,143,255,0.12);border-radius:10px;text-align:center;'>
    <div style='font-size:1.2rem;font-weight:800;color:#5b8aff;font-family:JetBrains Mono,monospace'>{step_num}</div>
    <div style='color:#2a3a58;font-size:0.65rem;text-transform:uppercase;letter-spacing:0.1em;font-weight:600'>Step</div>
  </div>
  <div style='flex:1;padding:10px 14px;background:rgba(13,18,48,0.9);border:1px solid rgba(108,143,255,0.12);border-radius:10px;text-align:center;'>
    <div style='font-size:1.2rem;font-weight:800;color:#a78bfa;font-family:JetBrains Mono,monospace'>{len(curr_arr)}</div>
    <div style='color:#2a3a58;font-size:0.65rem;text-transform:uppercase;letter-spacing:0.1em;font-weight:600'>Elements</div>
  </div>
  <div style='flex:2;padding:10px 14px;background:rgba(13,18,48,0.9);border:1px solid rgba(108,143,255,0.12);border-radius:10px;display:flex;align-items:center;gap:8px;'>
    <div style='width:8px;height:8px;border-radius:50%;background:{status_color};flex-shrink:0'></div>
    <div style='color:#7a9aff;font-size:0.78rem;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis'>{status_label}</div>
  </div>
</div>""", unsafe_allow_html=True)
        display_area.markdown(render_array_html(curr_arr, idx1, idx2, message, is_action), unsafe_allow_html=True)
        log_area.markdown(f"<div class='info-box'>&#128204; &nbsp;{message}</div>", unsafe_allow_html=True)
        if custom_lines is not None:
            msg_lower = message.lower()
            active = [i for i, l in enumerate(custom_lines) if any(w in l.lower() for w in msg_lower.split() if len(w) > 3)]
            code_html = render_code_panel(algo, active, custom_lines=custom_lines)
        else:
            code_html = render_code_panel(algo, get_active_lines(algo, message))
        exec_html = render_execution_panel(steps_log)
        panels_area.markdown(f"<div class='split-panel'>{code_html}{exec_html}</div>", unsafe_allow_html=True)
        time.sleep(1.0)
    st.balloons()


def run_graph_render(gen, algo, graph, node_pos):
    stat_area    = st.empty()
    graph_area   = st.empty()
    display_area = st.empty()
    log_area     = st.empty()
    panels_area  = st.empty()
    steps_log    = []
    step_num     = 0
    visited_so_far = set()
    current_node   = -1
    frontier       = []
    for step in gen:
        curr_arr, idx1, idx2, message, is_action = step
        step_num += 1
        steps_log.append((step_num, message, curr_arr))
        current_node = idx1 if idx1 != -1 else current_node
        if is_action and idx1 != -1:
            visited_so_far.add(idx1)
        frontier = []
        m = re.search(r'(?:Queue|Stack):\s*(\[[^\]]*\])', message)
        if m:
            try: frontier = eval(m.group(1))
            except: frontier = []
        is_done = any(k in message for k in ("Complete","complete","Done"))
        status_color = "#10c97a" if is_done else "#3d5af1"
        status_label = "&#9989; Done" if is_done else "&#9654; Running"
        stat_area.markdown(f"""
<div style='display:flex;gap:10px;margin-bottom:12px;'>
  <div style='flex:1;padding:10px 14px;background:rgba(13,18,48,0.9);border:1px solid rgba(108,143,255,0.12);border-radius:10px;text-align:center;'>
    <div style='font-size:1.2rem;font-weight:800;color:#5b8aff;font-family:JetBrains Mono,monospace'>{step_num}</div>
    <div style='color:#2a3a58;font-size:0.65rem;text-transform:uppercase;letter-spacing:0.1em;font-weight:600'>Step</div>
  </div>
  <div style='flex:1;padding:10px 14px;background:rgba(13,18,48,0.9);border:1px solid rgba(108,143,255,0.12);border-radius:10px;text-align:center;'>
    <div style='font-size:1.2rem;font-weight:800;color:#a78bfa;font-family:JetBrains Mono,monospace'>{len(visited_so_far)}</div>
    <div style='color:#2a3a58;font-size:0.65rem;text-transform:uppercase;letter-spacing:0.1em;font-weight:600'>Visited</div>
  </div>
  <div style='flex:1;padding:10px 14px;background:rgba(13,18,48,0.9);border:1px solid rgba(108,143,255,0.12);border-radius:10px;text-align:center;'>
    <div style='font-size:1.2rem;font-weight:800;color:#f0b429;font-family:JetBrains Mono,monospace'>{len(frontier)}</div>
    <div style='color:#2a3a58;font-size:0.65rem;text-transform:uppercase;letter-spacing:0.1em;font-weight:600'>Frontier</div>
  </div>
  <div style='flex:2;padding:10px 14px;background:rgba(13,18,48,0.9);border:1px solid rgba(108,143,255,0.12);border-radius:10px;display:flex;align-items:center;gap:8px;'>
    <div style='width:8px;height:8px;border-radius:50%;background:{status_color};flex-shrink:0'></div>
    <div style='color:#7a9aff;font-size:0.78rem;font-weight:600'>{status_label}</div>
  </div>
</div>""", unsafe_allow_html=True)
        svg_html = f"<div class='graph-container'>{render_graph_svg(graph, node_pos, visited_so_far, current_node if is_action else -1, frontier)}</div>"
        graph_area.markdown(svg_html, unsafe_allow_html=True)
        # visited order strip
        html = "<div class='array-container'>"
        for val in curr_arr:
            css = "array-element swap-element" if (val == current_node and is_action) else ("array-element active-element" if is_action else "array-element sorted-element")
            html += f"<div class='array-col'><div class='{css}'>{val}</div><span class='pointer-label pointer-none'>·</span></div>"
        if not curr_arr:
            html += "<div class='array-element' style='color:#4a5a80;font-style:italic;'>traversal starting…</div>"
        html += "</div>"
        display_area.markdown(html, unsafe_allow_html=True)
        log_area.markdown(f"<div class='info-box'>&#128204; &nbsp;{message}</div>", unsafe_allow_html=True)
        active_lines = get_active_lines(algo, message)
        code_html = render_code_panel(algo, active_lines)
        exec_html = render_execution_panel(steps_log)
        panels_area.markdown(f"<div class='split-panel'>{code_html}{exec_html}</div>", unsafe_allow_html=True)
        time.sleep(1.1)
    st.balloons()


CUSTOM_TEMPLATES = {
    "Array / List": {
        "Linear Search Style": '''\
# Available inputs: arr, target, n, context
def my_algorithm(arr, target, n, context):
    for i, value in enumerate(arr):
        yield emit_step(
            state=list(arr),
            idx1=i,
            message=f"Checking index {i}: {value}",
            is_action=False,
        )
        if value == target:
            yield emit_step(
                state=list(arr),
                idx1=i,
                message=f"Found {target} at index {i}",
                is_action=True,
            )
            return
    yield emit_step(state=list(arr), message=f"{target} not found", is_action=False)
''',
        "Bubble Sort Style": '''\
# Available inputs: arr, target, n, context
def my_algorithm(arr, target, n, context):
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            yield emit_step(
                state=list(arr),
                idx1=j,
                idx2=j + 1,
                message=f"Comparing {arr[j]} and {arr[j + 1]}",
                is_action=False,
            )
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
                yield emit_step(
                    state=list(arr),
                    idx1=j,
                    idx2=j + 1,
                    message=f"Swapped positions {j} and {j + 1}",
                    is_action=True,
                )
        if not swapped:
            break
    yield emit_step(state=list(arr), message="Custom algorithm complete!", is_action=True)
''',
    },
    "Graph Traversal": {
        "BFS Style": '''\
# Available inputs: graph, start, context
def my_algorithm(graph, start, context):
    visited = {start}
    queue = deque([start])
    order = []

    yield emit_step(
        state=list(order),
        current_node=start,
        frontier=list(queue),
        visited=visited,
        message=f"Starting traversal from {start}",
        is_action=False,
    )

    while queue:
        node = queue.popleft()
        order.append(node)
        yield emit_step(
            state=list(order),
            current_node=node,
            frontier=list(queue),
            visited=visited | {node},
            message=f"Visiting node {node}",
            is_action=True,
        )

        for neighbour in graph.get(node, []):
            if neighbour not in visited:
                visited.add(neighbour)
                queue.append(neighbour)
                yield emit_step(
                    state=list(order),
                    current_node=node,
                    frontier=list(queue),
                    visited=set(visited),
                    message=f"Queued neighbour {neighbour}",
                    is_action=False,
                )

    yield emit_step(
        state=list(order),
        frontier=[],
        visited=visited,
        message=f"Traversal complete: {order}",
        is_action=True,
    )
''',
        "DFS Style": '''\
# Available inputs: graph, start, context
def my_algorithm(graph, start, context):
    visited = set()
    stack = [start]
    order = []

    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        order.append(node)
        yield emit_step(
            state=list(order),
            current_node=node,
            frontier=list(stack),
            visited=set(visited),
            message=f"Visited {node}",
            is_action=True,
        )
        for neighbour in reversed(graph.get(node, [])):
            if neighbour not in visited:
                stack.append(neighbour)
                yield emit_step(
                    state=list(order),
                    current_node=node,
                    frontier=list(stack),
                    visited=set(visited),
                    message=f"Pushed {neighbour} to stack",
                    is_action=False,
                )

    yield emit_step(
        state=list(order),
        frontier=[],
        visited=visited,
        message=f"Traversal complete: {order}",
        is_action=True,
    )
''',
    },
}

CUSTOM_EDITOR_TEMPLATE = '''\
arr = [5, 3, 8, 1, 9, 2]
n = len(arr)

for i in range(n):
    for j in range(0, n - i - 1):
        if arr[j] > arr[j + 1]:
            arr[j], arr[j + 1] = arr[j + 1], arr[j]

print("Sorted:", arr)
'''


def emit_step(state=None, idx1=-1, idx2=-1, message="", is_action=False, **extra):
    payload = {
        "state": list(state) if state is not None else [],
        "idx1": idx1,
        "idx2": idx2,
        "message": message,
        "is_action": is_action,
    }
    payload.update(extra)
    return payload


def get_custom_active_lines(custom_lines, message):
    tokens = [token for token in re.findall(r"[A-Za-z_]+", str(message).lower()) if len(token) > 2]
    active = []
    for idx, line in enumerate(custom_lines):
        lowered = line.lower()
        if any(token in lowered for token in tokens):
            active.append(idx)
    return active


def normalize_custom_array_step(step, last_state):
    if isinstance(step, dict):
        state = step.get("state", last_state)
        idx1 = step.get("idx1", -1)
        idx2 = step.get("idx2", -1)
        message = str(step.get("message", "Custom step"))
        is_action = bool(step.get("is_action", False))
    elif isinstance(step, (list, tuple)) and len(step) == 5:
        state, idx1, idx2, message, is_action = step
    else:
        raise ValueError("Each custom array step must be a dict from emit_step(...) or a 5-item tuple.")
    return list(state), int(idx1), int(idx2), str(message), bool(is_action)


def normalize_custom_graph_step(step, last_state):
    if isinstance(step, dict):
        state = step.get("state", step.get("order", last_state))
        current_node = step.get("current_node", step.get("node", -1))
        frontier = list(step.get("frontier", []))
        visited = set(step.get("visited", state if state is not None else []))
        message = str(step.get("message", "Custom graph step"))
        is_action = bool(step.get("is_action", False))
    elif isinstance(step, (list, tuple)) and len(step) == 5:
        state, current_node, _, message, is_action = step
        frontier = []
        visited = set(state if state is not None else [])
    else:
        raise ValueError("Each custom graph step must be a dict from emit_step(...) or a 5-item tuple.")
    state = list(state) if state is not None else []
    if current_node is None:
        current_node = -1
    return {
        "state": state,
        "current_node": current_node,
        "frontier": frontier,
        "visited": visited,
        "message": message,
        "is_action": is_action,
    }


def infer_state_sequence(local_vars):
    preferred_names = ("arr", "array", "nums", "data", "values", "items", "lst", "list1", "result", "output")
    simple_types = (int, float, str, bool)

    def is_simple_sequence(value):
        return isinstance(value, (list, tuple, deque)) and all(isinstance(item, simple_types) for item in value)

    for name in preferred_names:
        value = local_vars.get(name)
        if is_simple_sequence(value):
            return list(value)

    for value in local_vars.values():
        if is_simple_sequence(value):
            return list(value)

    scalar_items = []
    for name, value in local_vars.items():
        if isinstance(value, simple_types) and name != "__builtins__":
            scalar_items.append(f"{name}={value}")
    return scalar_items[:12]


def infer_pointer_indexes(local_vars):
    pointer_map = {
        "i": ("i", "left", "low", "start", "ptr1"),
        "j": ("j", "right", "high", "end", "ptr2"),
    }
    inferred = []
    for names in pointer_map.values():
        idx = -1
        for name in names:
            value = local_vars.get(name)
            if isinstance(value, int):
                idx = value
                break
        inferred.append(idx)
    return inferred[0], inferred[1]


def is_adjacency_graph(value):
    if not isinstance(value, dict) or not value:
        return False
    sample_items = list(value.items())[:8]
    for key, neighbours in sample_items:
        if not isinstance(key, (int, str)):
            return False
        if not isinstance(neighbours, (list, tuple, set, deque)):
            return False
        if any(not isinstance(node, (int, str)) for node in list(neighbours)[:12]):
            return False
    return True


def infer_graph_trace_payload(local_vars):
    graph = None
    for key in ("graph", "adj", "adj_list", "adjacency", "adjacency_list", "g"):
        value = local_vars.get(key)
        if is_adjacency_graph(value):
            graph = {node: list(neighbours) for node, neighbours in value.items()}
            break
    if graph is None:
        for value in local_vars.values():
            if is_adjacency_graph(value):
                graph = {node: list(neighbours) for node, neighbours in value.items()}
                break
    if graph is None:
        return None

    current_node = -1
    for key in ("current_node", "node", "curr", "u", "v", "vertex", "src"):
        value = local_vars.get(key)
        if isinstance(value, (int, str)):
            current_node = value
            break

    frontier = []
    for key in ("queue", "stack", "frontier", "q"):
        value = local_vars.get(key)
        if isinstance(value, (list, tuple, deque)):
            frontier = list(value)
            break

    visited = local_vars.get("visited", set())
    if isinstance(visited, (set, list, tuple, deque)):
        visited = set(visited)
    else:
        visited = set()

    state = []
    for key in ("order", "path", "result", "traversal", "bfs_order", "dfs_order", "answer"):
        value = local_vars.get(key)
        if isinstance(value, (list, tuple, deque)):
            state = list(value)
            break
    if not state and visited:
        state = list(visited)

    if current_node == -1 and not frontier and not visited and not state:
        return None

    return {
        "graph": graph,
        "state": state,
        "current_node": current_node,
        "frontier": frontier,
        "visited": visited,
    }


def trace_plain_python_code(user_code, runtime_inputs):
    filename = "<custom_exec>"
    source_lines = user_code.splitlines()
    steps = []
    namespace = {
        "deque": deque,
        "np": np,
        "re": re,
        "emit_step": emit_step,
    }
    namespace.update(runtime_inputs)

    def make_message(lineno):
        line_text = source_lines[lineno - 1].strip() if 0 < lineno <= len(source_lines) else ""
        return f"Line {lineno}: {line_text}" if line_text else f"Line {lineno}"

    def build_error_step(lineno, local_vars, error_text):
        graph_payload = infer_graph_trace_payload(local_vars)
        if graph_payload is not None:
            return {
                **graph_payload,
                "message": error_text,
                "is_action": False,
                "line_no": lineno,
            }
        state = infer_state_sequence(local_vars)
        idx1, idx2 = infer_pointer_indexes(local_vars)
        return {
            "state": state,
            "idx1": idx1,
            "idx2": idx2,
            "message": error_text,
            "is_action": False,
            "line_no": lineno,
        }

    def tracer(frame, event, arg):
        if frame.f_code.co_filename != filename:
            return tracer
        if event == "line":
            local_vars = dict(frame.f_locals)
            graph_payload = infer_graph_trace_payload(local_vars)
            if graph_payload is not None:
                steps.append({
                    **graph_payload,
                    "message": make_message(frame.f_lineno),
                    "is_action": True,
                    "line_no": frame.f_lineno,
                })
            else:
                state = infer_state_sequence(local_vars)
                idx1, idx2 = infer_pointer_indexes(local_vars)
                steps.append({
                    "state": state,
                    "idx1": idx1,
                    "idx2": idx2,
                    "message": make_message(frame.f_lineno),
                    "is_action": True,
                    "line_no": frame.f_lineno,
                })
        return tracer

    try:
        compiled = compile(user_code, filename, "exec")
        previous_tracer = sys.gettrace()
        sys.settrace(tracer)
        try:
            exec(compiled, namespace, namespace)
        finally:
            sys.settrace(previous_tracer)
    except SyntaxError as exc:
        return None, f"Wrong algorithm. Incorrect step at line {exc.lineno}: {exc.msg}"
    except Exception as exc:
        tb = exc.__traceback__
        target_tb = None
        while tb is not None:
            if tb.tb_frame.f_code.co_filename == filename:
                target_tb = tb
            tb = tb.tb_next
        if target_tb is not None:
            lineno = target_tb.tb_lineno
            line_text = source_lines[lineno - 1].strip() if 0 < lineno <= len(source_lines) else ""
            steps.append(build_error_step(
                lineno,
                dict(target_tb.tb_frame.f_locals),
                f"Incorrect step at line {lineno}: {line_text} ({exc})",
            ))
            return iter(steps), None
        return None, f"Wrong algorithm. Runtime error: {exc}"

    final_graph_payload = infer_graph_trace_payload(namespace)
    if final_graph_payload is not None:
        steps.append({
            **final_graph_payload,
            "message": "Execution complete",
            "is_action": True,
            "line_no": len(source_lines),
        })
    else:
        state = infer_state_sequence(namespace)
        idx1, idx2 = infer_pointer_indexes(namespace)
        steps.append({
            "state": state,
            "idx1": idx1,
            "idx2": idx2,
            "message": "Execution complete",
            "is_action": True,
            "line_no": len(source_lines),
        })

    if not steps:
        return None, "Wrong algorithm. Nothing to simulate from this code."
    return iter(steps), None


def run_custom_algorithm(user_code, mode, runtime_inputs):
    try:
        parsed = ast.parse(user_code, filename="<custom>")
    except SyntaxError as exc:
        return None, f"SyntaxError on line {exc.lineno}: {exc.msg}"

    has_custom_function = any(
        isinstance(node, ast.FunctionDef) and node.name == "my_algorithm"
        for node in ast.walk(parsed)
    )
    if not has_custom_function:
        return trace_plain_python_code(user_code, runtime_inputs)

    namespace = {
        "deque": deque,
        "np": np,
        "re": re,
        "emit_step": emit_step,
    }
    namespace.update(runtime_inputs)
    try:
        exec(compile(user_code, "<custom>", "exec"), namespace)
    except SyntaxError as exc:
        return None, f"SyntaxError on line {exc.lineno}: {exc.msg}"
    except Exception as exc:
        return None, f"Error during compile: {exc}"

    custom_fn = namespace.get("my_algorithm")
    if custom_fn is None:
        return None, "No function named `my_algorithm` found. Please define it."

    available_args = {
        "arr": list(runtime_inputs.get("arr", [])),
        "target": runtime_inputs.get("target", 0),
        "n": len(runtime_inputs.get("arr", [])),
        "graph": runtime_inputs.get("graph", {}),
        "start": runtime_inputs.get("start", 0),
        "context": runtime_inputs.get("context", {}),
        "deque": deque,
        "emit_step": emit_step,
    }
    try:
        params = inspect.signature(custom_fn).parameters
        kwargs = {name: available_args[name] for name in params if name in available_args}
        result = custom_fn(**kwargs)
    except Exception as exc:
        return None, f"Error calling my_algorithm: {exc}"

    if result is None or not hasattr(result, "__iter__"):
        return None, f"`my_algorithm` must return a generator or iterable of steps for {mode.lower()} mode."
    return iter(result), None


def run_custom_standard_render(gen, algo, custom_lines):
    display_area = st.empty()
    log_area = st.empty()
    st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)
    panels_area = st.empty()
    steps_log = []
    step_num = 0
    last_state = []

    try:
        for raw_step in gen:
            curr_arr, idx1, idx2, message, is_action = normalize_custom_array_step(raw_step, last_state)
            last_state = list(curr_arr)
            step_num += 1
            steps_log.append((step_num, message, curr_arr))
            display_area.markdown(render_array_html(curr_arr, idx1, idx2, message, is_action), unsafe_allow_html=True)
            log_area.markdown(f"<div class='info-box'>{message}</div>", unsafe_allow_html=True)
            if isinstance(raw_step, dict) and isinstance(raw_step.get("line_no"), int):
                active_lines = [max(0, raw_step["line_no"] - 1)]
            else:
                active_lines = get_custom_active_lines(custom_lines, message)
            code_html = render_code_panel(algo, active_lines, custom_lines=custom_lines)
            exec_html = render_execution_panel(steps_log)
            panels_area.markdown(f"<div class='split-panel'>{code_html}{exec_html}</div>", unsafe_allow_html=True)
            time.sleep(1.0)
    except Exception as exc:
        st.markdown(f"<div class='error-box'>Runtime error while executing custom steps: {exc}</div>", unsafe_allow_html=True)
        return
    st.balloons()


def run_custom_graph_render(gen, algo, graph, node_pos, custom_lines):
    graph_area = st.empty()
    display_area = st.empty()
    log_area = st.empty()
    panels_area = st.empty()
    steps_log = []
    step_num = 0
    last_state = []

    try:
        for raw_step in gen:
            step = normalize_custom_graph_step(raw_step, last_state)
            curr_arr = step["state"]
            last_state = list(curr_arr)
            step_num += 1
            steps_log.append((step_num, step["message"], curr_arr))
            svg_html = f"<div class='graph-container'>{render_graph_svg(graph, node_pos, step['visited'], step['current_node'], step['frontier'])}</div>"
            graph_area.markdown(svg_html, unsafe_allow_html=True)

            html = "<div class='array-container'>"
            for val in curr_arr:
                css = "array-element swap-element" if (val == step["current_node"] and step["is_action"]) else ("array-element active-element" if step["is_action"] else "array-element sorted-element")
                html += f"<div class='array-col'><div class='{css}'>{val}</div><span class='pointer-label pointer-none'>.</span></div>"
            if not curr_arr:
                html += "<div class='array-element' style='color:#8b949e'>-- traversal starting --</div>"
            html += "</div>"
            display_area.markdown(html, unsafe_allow_html=True)

            log_area.markdown(f"<div class='info-box'>{step['message']}</div>", unsafe_allow_html=True)
            if isinstance(raw_step, dict) and isinstance(raw_step.get("line_no"), int):
                active_lines = [max(0, raw_step["line_no"] - 1)]
            else:
                active_lines = get_custom_active_lines(custom_lines, step["message"])
            code_html = render_code_panel(algo, active_lines, custom_lines=custom_lines)
            exec_html = render_execution_panel(steps_log)
            panels_area.markdown(f"<div class='split-panel'>{code_html}{exec_html}</div>", unsafe_allow_html=True)
            time.sleep(1.1)
    except Exception as exc:
        st.markdown(f"<div class='error-box'>Runtime error while executing custom graph steps: {exc}</div>", unsafe_allow_html=True)
        return
    st.balloons()


# ─────────────────────────────────────────────────────────────────────────────
# MAIN UI
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@keyframes twinkle1 { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.2;transform:scale(0.5)} }
@keyframes twinkle2 { 0%,100%{opacity:0.6;transform:scale(0.8)} 50%{opacity:1;transform:scale(1.2)} }
@keyframes twinkle3 { 0%,100%{opacity:0.3;transform:scale(1)} 33%{opacity:1;transform:scale(1.3)} 66%{opacity:0.5;transform:scale(0.7)} }
.star { position:absolute; border-radius:50%; background:#fff; pointer-events:none; }
</style>
<div style='background:linear-gradient(120deg,#05103a 0%,#071845 35%,#0a1f55 60%,#071845 80%,#05103a 100%);border:1px solid rgba(80,120,255,0.28);border-radius:20px;padding:28px 32px 24px;margin-bottom:24px;position:relative;overflow:hidden;'>
  <!-- Nebula glows -->
  <div style='position:absolute;top:-40px;right:-40px;width:200px;height:200px;border-radius:50%;background:radial-gradient(circle,rgba(80,40,180,0.18),transparent 70%);pointer-events:none'></div>
  <div style='position:absolute;bottom:-30px;left:20%;width:160px;height:160px;border-radius:50%;background:radial-gradient(circle,rgba(40,70,200,0.14),transparent 70%);pointer-events:none'></div>
  <div style='position:absolute;top:10px;left:40%;width:100px;height:100px;border-radius:50%;background:radial-gradient(circle,rgba(50,130,220,0.08),transparent 70%);pointer-events:none'></div>
  <!-- Stars -->
  <div class='star' style='width:2px;height:2px;top:12%;left:8%;animation:twinkle1 2.1s infinite'></div>
  <div class='star' style='width:3px;height:3px;top:25%;left:15%;animation:twinkle2 3.4s infinite'></div>
  <div class='star' style='width:1.5px;height:1.5px;top:60%;left:5%;animation:twinkle3 2.8s infinite'></div>
  <div class='star' style='width:2px;height:2px;top:75%;left:22%;animation:twinkle1 1.9s infinite 0.5s'></div>
  <div class='star' style='width:2.5px;height:2.5px;top:18%;left:35%;animation:twinkle2 2.6s infinite 0.3s'></div>
  <div class='star' style='width:1.5px;height:1.5px;top:80%;left:42%;animation:twinkle3 3.1s infinite 1s'></div>
  <div class='star' style='width:3px;height:3px;top:10%;left:55%;animation:twinkle1 2.4s infinite 0.7s'></div>
  <div class='star' style='width:2px;height:2px;top:55%;left:62%;animation:twinkle2 1.8s infinite 0.2s'></div>
  <div class='star' style='width:1.5px;height:1.5px;top:30%;left:72%;animation:twinkle3 2.9s infinite 1.2s'></div>
  <div class='star' style='width:2.5px;height:2.5px;top:70%;left:78%;animation:twinkle1 3.2s infinite 0.4s'></div>
  <div class='star' style='width:2px;height:2px;top:15%;left:88%;animation:twinkle2 2.2s infinite 0.9s'></div>
  <div class='star' style='width:1.5px;height:1.5px;top:45%;left:93%;animation:twinkle3 2.5s infinite 0.6s'></div>
  <div class='star' style='width:3px;height:3px;top:85%;left:90%;animation:twinkle1 1.7s infinite 1.4s'></div>
  <div class='star' style='width:2px;height:2px;top:40%;left:28%;animation:twinkle2 3.0s infinite 0.1s'></div>
  <div class='star' style='width:1.5px;height:1.5px;top:90%;left:50%;animation:twinkle3 2.3s infinite 0.8s'></div>
  <!-- Content -->
  <div style='display:flex;align-items:center;gap:16px;position:relative'>
    <div style='width:52px;height:52px;border-radius:14px;background:linear-gradient(135deg,#3d5af1,#6c3dd4);display:flex;align-items:center;justify-content:center;font-size:1.6rem;box-shadow:0 6px 24px rgba(61,90,241,0.6);flex-shrink:0;'>&#9889;</div>
    <div>
      <div style='font-size:1.9rem;font-weight:800;color:#d0e4ff;letter-spacing:-0.03em;line-height:1.1;'>AlgoMentor <span style='color:#7b9fff;font-weight:400;font-size:1.1rem;'>Visualizer</span></div>
      <div style='color:#3d5580;font-size:0.83rem;letter-spacing:0.05em;margin-top:4px;'>&#9679; Build Algorithmic Thinking &nbsp;&nbsp;&#9679; Visual Step-by-Step &nbsp;&nbsp;&#9679; Adaptive Feedback</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)
st.sidebar.markdown("""
<div style='display:flex;align-items:center;gap:8px;padding:14px 0 6px'>
  <div style='width:32px;height:32px;border-radius:9px;background:linear-gradient(135deg,#3d5af1,#6c3dd4);display:flex;align-items:center;justify-content:center;font-size:1rem;box-shadow:0 3px 10px rgba(61,90,241,0.4)'>&#9889;</div>
  <div>
    <div style='color:#b8ceff;font-weight:800;font-size:1rem;letter-spacing:-0.01em;line-height:1.1'>AlgoMentor</div>
    <div style='color:#3a4a70;font-size:0.68rem;letter-spacing:0.06em'>VISUALIZER</div>
  </div>
</div>
<div style='height:1px;background:linear-gradient(90deg,rgba(108,143,255,0.3),transparent);margin:10px 0 16px'></div>
<div style='color:#3a4a6a;font-size:0.68rem;letter-spacing:0.12em;text-transform:uppercase;font-weight:700;margin-bottom:10px'>&#8250; Algorithm Settings</div>
""", unsafe_allow_html=True)

category = st.sidebar.selectbox(
    "Select Category",
    ("Sorting", "Searching", "Basic Algorithms", "Graph Traversal", "✏️ Custom Algorithm")
)

_cat_desc = {
    "Sorting": ("&#127922;", "Compare how arrays transform step‑by‑step through swaps & comparisons."),
    "Searching": ("&#128269;", "Watch pointers narrow in on your target through the array."),
    "Basic Algorithms": ("&#128218;", "Explore hash maps, stacks, and dynamic programming patterns."),
    "Graph Traversal": ("&#127760;", "See BFS & DFS explore nodes layer by layer or depth first."),
    "✏️ Custom Algorithm": ("&#9998;", "Write your own Python generator and watch it come alive."),
}
_icon, _desc = _cat_desc.get(category, ("&#128301;", ""))
st.sidebar.markdown(f"""
<div style='margin-top:8px;margin-bottom:4px;padding:10px 12px;background:rgba(61,90,241,0.07);border:1px solid rgba(108,143,255,0.13);border-radius:10px;'>
  <span style='font-size:1.1rem'>{_icon}</span>
  <span style='color:#5a7aaa;font-size:0.78rem;line-height:1.4;margin-left:6px'>{_desc}</span>
</div>
""", unsafe_allow_html=True)

gen         = None
algo        = ""
is_graph    = False
graph_obj   = None
node_pos    = None
custom_lines_for_render = None
custom_mode = None
custom_graph_obj = None
custom_node_pos = None
custom_render_kind = None

# ── SORTING ───────────────────────────────────────────────────────────────────
if category == "Sorting":
    algo = st.sidebar.selectbox("Algorithm", ("Bubble Sort", "Selection Sort", "Insertion Sort"))
    data_input = st.sidebar.text_input("Numbers (comma-separated)", "64, 34, 25, 12, 22")
    if st.sidebar.button("Run Sorting"):
        arr = [int(x.strip()) for x in data_input.split(",")]
        if algo == "Bubble Sort":      gen = bubble_sort_visualizer(arr)
        elif algo == "Selection Sort": gen = selection_sort_visualizer(arr)
        elif algo == "Insertion Sort": gen = insertion_sort_visualizer(arr)

# ── SEARCHING ─────────────────────────────────────────────────────────────────
elif category == "Searching":
    algo = st.sidebar.selectbox("Algorithm", ("Linear Search", "Binary Search"))
    data_input = st.sidebar.text_input("Numbers (Sorted for Binary)", "10, 20, 30, 40, 50")
    target = st.sidebar.number_input("Target", value=30)
    if st.sidebar.button("Run Search"):
        arr = [int(x.strip()) for x in data_input.split(",")]
        if algo == "Linear Search":   gen = linear_search_visualizer(arr, target)
        elif algo == "Binary Search": gen = binary_search_visualizer(arr, target)

# ── BASIC ALGORITHMS  (now with full user input) ─────────────────────────────
elif category == "Basic Algorithms":
    algo = st.sidebar.selectbox("Algorithm", ("Two Sum", "Valid Parentheses", "Fibonacci DP", "Reverse List"))

    if algo == "Two Sum":
        st.sidebar.markdown("**Input numbers** (space or comma separated):")
        nums_input  = st.sidebar.text_input("Numbers", "2, 7, 11, 15")
        target_2sum = st.sidebar.number_input("Target sum", value=9)
        if st.sidebar.button("Run Visualization"):
            try:
                nums = [int(x.strip()) for x in re.split(r"[,\s]+", nums_input.strip()) if x.strip()]
                gen  = two_sum_visualizer(nums, int(target_2sum))
            except Exception as e:
                st.error(f"Invalid input: {e}")

    elif algo == "Valid Parentheses":
        st.sidebar.markdown("**Bracket string** (e.g. `({[]})`):")
        paren_input = st.sidebar.text_input("String", "({[]})")
        if st.sidebar.button("Run Visualization"):
            gen = valid_parentheses_visualizer(paren_input.strip())

    elif algo == "Fibonacci DP":
        st.sidebar.markdown("**Compute Fibonacci up to N:**")
        fib_n = st.sidebar.number_input("N", min_value=1, max_value=30, value=7, step=1)
        if st.sidebar.button("Run Visualization"):
            gen = fibonacci_dp_visualizer(int(fib_n))

    elif algo == "Reverse List":
        st.sidebar.markdown("**List to reverse** (comma separated):")
        rev_input = st.sidebar.text_input("List", "1, 2, 3, 4, 5")
        if st.sidebar.button("Run Visualization"):
            try:
                rev_arr = [int(x.strip()) for x in rev_input.split(",") if x.strip()]
                gen     = reverse_linked_list_visualizer(rev_arr)
            except Exception as e:
                st.error(f"Invalid input: {e}")

# ── GRAPH TRAVERSAL  (now with custom graph input) ────────────────────────────
elif category == "Graph Traversal":
    algo = st.sidebar.selectbox("Algorithm", ("BFS", "DFS"))
    is_graph = True

    graph_mode = st.sidebar.radio("Graph input", ("Use default graph", "Enter custom graph"))

    DEFAULT_GRAPH_TEXT = "0: 1 2\n1: 0 3 4\n2: 0 5 6\n3: 1\n4: 1\n5: 2\n6: 2"

    if graph_mode == "Use default graph":
        raw_graph_text = DEFAULT_GRAPH_TEXT
        st.sidebar.markdown("""
**Default graph:**
```
    0
   / \\
  1   2
 / \\ / \\
3  4 5  6
```
""")
    else:
        st.sidebar.markdown("""
**Enter adjacency list** (one node per line):
```
node: neighbour1 neighbour2 ...
```
""")
        raw_graph_text = st.sidebar.text_area("Adjacency list", DEFAULT_GRAPH_TEXT, height=160)

    try:
        graph_obj = parse_graph_input(raw_graph_text)
        node_pos  = compute_node_positions(graph_obj)
        start_node = st.sidebar.selectbox("Start Node", sorted(graph_obj.keys()), index=0)
        if st.sidebar.button("Run Graph Traversal"):
            if algo == "BFS": gen = bfs_visualizer(graph_obj, start_node)
            elif algo == "DFS": gen = dfs_visualizer(graph_obj, start_node)
    except ValueError as e:
        st.sidebar.error(f"Graph parse error: {e}")

# ── CUSTOM ALGORITHM ──────────────────────────────────────────────────────────
else:
    algo = "Custom"
    _legacy_custom_editor = '''
    st.sidebar.markdown("**Input data for your algorithm:**")
    custom_arr_input    = st.sidebar.text_input("Array (comma-separated)", "5, 3, 8, 1, 9, 2")
    custom_target_input = st.sidebar.number_input("Target (optional)", value=0)

    st.markdown("""
<div style='display:flex;align-items:center;gap:10px;margin-bottom:16px;padding:12px 18px;background:linear-gradient(135deg,rgba(26,125,224,0.08),rgba(13,155,214,0.05));border:1px solid rgba(26,111,191,0.2);border-radius:12px;box-shadow:0 2px 8px rgba(26,111,191,0.07);'>
  <span style='font-size:1.1rem'>&#9998;</span>
  <span style='color:#1a3a5c;font-size:1.1rem;font-weight:700;'>Custom Algorithm Editor</span>
</div>""", unsafe_allow_html=True)
    st.markdown("""
<div class='hint-box'>
<b>How it works:</b> Write a Python generator function called <b>my_algorithm(arr, target, n)</b>.<br>
Use <b>yield</b> to emit each step: <code>yield state_list, idx1, idx2, "message", is_swap</code><br>
• <b>state_list</b> — list of values to show in the array bar<br>
• <b>idx1</b> — index to highlight blue (i pointer), or -1<br>
• <b>idx2</b> — index to highlight red (j pointer), or -1<br>
• <b>message</b> — text shown in the info box below the array<br>
• <b>is_swap</b> — True = red highlight (swap), False = yellow (compare)
</div>
""", unsafe_allow_html=True)

    user_code = st.text_area(
        "Your algorithm code",
        value=CUSTOM_TEMPLATE,
        height=340,
        help="Write your generator here"
    )

    if st.button("▶ Run My Algorithm"):
        try:
            custom_arr = [int(x.strip()) for x in custom_arr_input.split(",") if x.strip()]
            custom_target = int(custom_target_input)
            gen, err = run_custom_algorithm(user_code, custom_arr, custom_target)
            if err:
                st.markdown(f"<div class='error-box'>❌ {err}</div>", unsafe_allow_html=True)
                gen = None
            else:
                custom_lines_for_render = user_code.splitlines()
        except Exception as e:
            st.error(f"Input error: {e}")
            gen = None
    '''
    editor_key = "custom_code_editor_minimal"
    if editor_key not in st.session_state:
        st.session_state[editor_key] = CUSTOM_EDITOR_TEMPLATE

    user_code = st.text_area(
        "Algorithm Editor",
        key=editor_key,
        height=420
    )

    if st.button("Run Algorithm"):
        try:
            runtime_inputs = {
                "arr": [],
                "target": 0,
                "graph": {},
                "start": 0,
                "context": {},
            }
            gen, err = run_custom_algorithm(user_code, "custom", runtime_inputs)
            if err:
                st.markdown(f"<div class='error-box'>Error: {err}</div>", unsafe_allow_html=True)
                gen = None
            else:
                steps = list(gen)
                if not steps:
                    st.markdown("<div class='error-box'>Wrong algorithm.</div>", unsafe_allow_html=True)
                    gen = None
                else:
                    graph_steps = [
                        step for step in steps
                        if isinstance(step, dict) and step.get("graph")
                    ]
                    custom_render_kind = "graph" if graph_steps else "array"
                    if graph_steps:
                        custom_graph_obj = graph_steps[0].get("graph")
                        if custom_graph_obj:
                            custom_node_pos = compute_node_positions(custom_graph_obj)
                    gen = iter(steps)
                    custom_lines_for_render = user_code.splitlines()
        except Exception as exc:
            st.error(f"Input error: {exc}")
            gen = None


# ─────────────────────────────────────────────────────────────────────────────
# DISPATCH TO RENDERER
# ─────────────────────────────────────────────────────────────────────────────
if not gen and category != "✏️ Custom Algorithm":
    _algo_chips = {
        "Sorting":          [("Bubble Sort","#f25c78"), ("Selection Sort","#f0b429"), ("Insertion Sort","#a78bfa")],
        "Searching":        [("Linear Search","#5b8aff"), ("Binary Search","#10c97a")],
        "Basic Algorithms": [("Two Sum","#f0b429"), ("Valid Parentheses","#10c97a"), ("Fibonacci DP","#a78bfa"), ("Reverse List","#5b8aff")],
        "Graph Traversal":  [("BFS","#5b8aff"), ("DFS","#f25c78")],
    }
    chips = _algo_chips.get(category, [])
    chips_html = "".join(
        f"<span style='display:inline-block;padding:5px 14px;border-radius:20px;font-size:0.8rem;font-weight:600;"
        f"background:rgba(255,255,255,0.7);border:1px solid {c}66;color:{c};margin:4px 6px 4px 0;box-shadow:0 1px 4px rgba(26,111,191,0.08);'>{n}</span>"
        for n, c in chips
    )
    st.markdown(f"""
<div style='margin-top:8px;padding:32px 28px;background:linear-gradient(135deg,rgba(255,255,255,0.97),rgba(235,247,255,0.95));border:1px solid rgba(26,111,191,0.15);border-radius:20px;text-align:center;box-shadow:0 4px 20px rgba(26,111,191,0.1);'>
  <div style='font-size:2.8rem;margin-bottom:14px'>&#127760;</div>
  <div style='color:#1a3a5c;font-size:1.25rem;font-weight:700;letter-spacing:-0.02em;margin-bottom:6px'>Ready to Visualize</div>
  <div style='color:#5a8ab0;font-size:0.85rem;margin-bottom:20px'>Configure an algorithm in the sidebar and hit Run</div>
  <div style='margin-bottom:8px'>{chips_html}</div>
  <div style='margin-top:22px;display:flex;justify-content:center;gap:24px;'>
    <div style='text-align:center'>
      <div style='font-size:1.5rem;font-weight:800;color:#1a7de0;font-family:JetBrains Mono,monospace'>12+</div>
      <div style='color:#5a8ab0;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;font-weight:600'>Algorithms</div>
    </div>
    <div style='width:1px;background:rgba(26,111,191,0.15)'></div>
    <div style='text-align:center'>
      <div style='font-size:1.5rem;font-weight:800;color:#2196f3;font-family:JetBrains Mono,monospace'>Live</div>
      <div style='color:#5a8ab0;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;font-weight:600'>Step Trace</div>
    </div>
    <div style='width:1px;background:rgba(26,111,191,0.15)'></div>
    <div style='text-align:center'>
      <div style='font-size:1.5rem;font-weight:800;color:#10c97a;font-family:JetBrains Mono,monospace'>2-col</div>
      <div style='color:#5a8ab0;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;font-weight:600'>Code + Log</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

if gen:
    if algo not in ("Custom",):
        st.markdown(f"""
<div style='display:flex;align-items:center;gap:12px;margin-bottom:16px;padding:14px 20px;background:linear-gradient(135deg,rgba(26,125,224,0.08),rgba(13,155,214,0.05));border:1px solid rgba(26,111,191,0.2);border-radius:14px;box-shadow:0 2px 10px rgba(26,111,191,0.08);'>
  <div style='width:8px;height:8px;border-radius:50%;background:#1a7de0;box-shadow:0 0 10px rgba(26,125,224,0.6);animation:pulse 1.5s infinite'></div>
  <span style='color:#1a6fbf;font-size:0.7rem;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;'>Now Visualizing</span>
  <div style='width:1px;height:16px;background:rgba(26,111,191,0.25)'></div>
  <span style='color:#1a3a5c;font-size:1.15rem;font-weight:700;letter-spacing:-0.01em;'>{algo}</span>
</div>""", unsafe_allow_html=True)

    if custom_render_kind == "graph" and custom_lines_for_render is not None:
        if not custom_graph_obj:
            st.markdown("<div class='error-box'>Wrong algorithm.</div>", unsafe_allow_html=True)
        else:
            run_custom_graph_render(gen, algo, custom_graph_obj, custom_node_pos, custom_lines_for_render)
    elif custom_lines_for_render is not None:
        run_custom_standard_render(gen, algo, custom_lines_for_render)
    elif is_graph and graph_obj and node_pos:
        run_graph_render(gen, algo, graph_obj, node_pos)
    else:
        run_standard_render(gen, algo)
