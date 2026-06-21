from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Dataset Loading
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[2]
DATASET_PATH = BASE_DIR / "Datasets" / "understanding_dataset.json"

_DATASET_CACHE: list[dict[str, Any]] | None = None


def _load_dataset() -> list[dict[str, Any]]:
    """Load and cache the understanding dataset."""
    global _DATASET_CACHE
    if _DATASET_CACHE is not None:
        return _DATASET_CACHE

    if not DATASET_PATH.exists():
        _DATASET_CACHE = []
        return _DATASET_CACHE

    try:
        data = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        _DATASET_CACHE = []
        return _DATASET_CACHE

    # Parse each entry: extract problem name and thought separately
    parsed = []
    for item in data:
        if not isinstance(item, dict) or "input" not in item or "label" not in item:
            continue
        raw_input = item["input"]
        problem = ""
        thought = raw_input

        # Extract "Problem: X | Thought: Y"
        match = re.match(r"Problem:\s*(.+?)\s*\|\s*Thought:\s*(.+)", raw_input, re.DOTALL)
        if match:
            problem = match.group(1).strip().lower()
            thought = match.group(2).strip()

        parsed.append({
            "problem": problem,
            "thought": thought,
            "label": item["label"],
            "features": _feature_set(thought),
        })

    _DATASET_CACHE = parsed
    return _DATASET_CACHE


# ---------------------------------------------------------------------------
# Text Processing — extracts meaning from full sentences
# ---------------------------------------------------------------------------

# Common filler words that don't carry algorithmic meaning
_STOP_WORDS = frozenset({
    "i", "we", "a", "an", "the", "is", "it", "to", "in", "of", "and", "or",
    "but", "that", "this", "with", "for", "on", "at", "by", "be", "as",
    "do", "if", "so", "my", "me", "can", "will", "am", "are", "was",
    "has", "have", "had", "not", "no", "just", "also", "like", "here",
    "there", "then", "than", "from", "about", "some", "would", "should",
    "could", "does", "did", "its", "our", "they", "them", "what", "when",
    "how", "which", "who", "very", "too", "more", "most", "all", "any",
    "each", "both", "such", "been", "being", "because", "between",
    "these", "those", "after", "before", "into", "through", "during",
    "above", "below", "up", "down", "out", "off", "over", "under",
    "again", "once", "only", "own", "same", "other", "while",
    "think", "guess", "feel", "seems", "tho", "though", "idk",
    "maybe", "sure", "try", "know", "seems", "right", "correct",
    "something", "work", "works", "might", "yeah", "yes",
})


def _tokenize(text: str) -> list[str]:
    """Break text into meaningful lowercase word tokens."""
    return [
        w for w in re.findall(r"[a-z]{2,}", text.lower())
        if w not in _STOP_WORDS
    ]


def _bigrams(tokens: list[str]) -> set[str]:
    """Generate bigrams (two-word phrases) to capture phrase-level meaning."""
    return {f"{tokens[i]}_{tokens[i+1]}" for i in range(len(tokens) - 1)}


def _feature_set(text: str) -> set[str]:
    """
    Build a feature set from text using both unigrams and bigrams.
    Bigrams capture phrase meaning — e.g. "graph_traversal" vs just "graph".
    """
    tokens = _tokenize(text)
    features = set(tokens)
    features.update(_bigrams(tokens))
    return features


# ---------------------------------------------------------------------------
# Similarity — compares full sentence meaning, not just keywords
# ---------------------------------------------------------------------------

def _similarity(features_a: set[str], features_b: set[str]) -> float:
    """
    Compute similarity between two feature sets.
    Uses a weighted Jaccard: intersection / min(len_a, len_b)
    so that short student inputs aren't penalized for having fewer words
    than the longer dataset entries.
    """
    if not features_a or not features_b:
        return 0.0
    intersection = features_a & features_b
    # Use the smaller set size as denominator so short inputs get fair scores
    denominator = min(len(features_a), len(features_b))
    return len(intersection) / denominator if denominator > 0 else 0.0


# ---------------------------------------------------------------------------
# Confusion / Vagueness Detection
# ---------------------------------------------------------------------------

def _is_confused_or_vague(text: str) -> bool:
    """
    Check if the student's text expresses confusion or is too vague
    to demonstrate any understanding. This checks the full phrase patterns.
    """
    text_lower = text.lower()

    # Strong confusion signals — full phrases, not keywords
    confusion_phrases = [
        "don't know",
        "dont know",
        "do not know",
        "no idea",
        "no clue",
        "clueless",
        "completely lost",
        "totally confused",
        "not sure what",
        "have no idea",
        "struggling",
        "hard time understanding",
    ]
    if any(phrase in text_lower for phrase in confusion_phrases):
        return True

    # Vague responses that show no algorithmic thinking
    meaningful_tokens = _tokenize(text)
    if len(meaningful_tokens) < 2:
        return True

    return False


# ---------------------------------------------------------------------------
# Prediction — instance-based retrieval with majority voting
# ---------------------------------------------------------------------------

def predict(text: Any, problem: str = "") -> dict[str, str]:
    """
    Evaluates student approach explanation using instance-based retrieval.

    Instead of checking keywords, this model:
    1. Checks if the student is expressing confusion (phrase-level, not keyword)
    2. Converts the student's full sentence into a feature set (words + phrases)
    3. Compares it against labeled examples in the dataset, boosting same-problem matches
    4. Finds the top-k most similar examples
    5. Uses majority voting on their labels to decide PROCEED or WATCH

    Args:
        text: The student's explanation/approach
        problem: Optional problem name (e.g. "two sum") for context-aware matching
    """
    text_str = str(text or "").strip()

    # Very short or empty input
    if len(text_str) < 3:
        return {"prediction": "WATCH"}

    # Check for confusion/vagueness using full phrase patterns
    if _is_confused_or_vague(text_str):
        return {"prediction": "WATCH"}

    dataset = _load_dataset()

    # If dataset is missing, fall back
    if not dataset:
        return {"prediction": "PROCEED" if len(text_str) >= 30 else "WATCH"}

    # Build feature set from the student's full sentence
    student_features = _feature_set(text_str)

    if not student_features:
        return {"prediction": "WATCH"}

    problem_lower = str(problem).strip().lower()

    # Score every dataset example by similarity to the student's sentence
    scored: list[tuple[float, str]] = []
    for entry in dataset:
        base_score = _similarity(student_features, entry["features"])
        if base_score <= 0:
            continue

        # Boost score if the problem matches — this helps the model
        # understand that "use hashmap" is correct for Two Sum but
        # wrong for Binary Search
        if problem_lower and entry["problem"]:
            if problem_lower in entry["problem"] or entry["problem"] in problem_lower:
                base_score *= 2.0  # Strong boost for same-problem entries
            else:
                base_score *= 0.5  # Penalize different-problem entries

        scored.append((base_score, entry["label"]))

    # If nothing matched at all, the student's input is too different
    if not scored:
        return {"prediction": "WATCH"}

    # Sort by similarity (highest first) and take top-k
    scored.sort(key=lambda x: x[0], reverse=True)
    top_k = 7
    top_matches = scored[:top_k]

    # Majority voting
    proceed_count = sum(1 for _, label in top_matches if label == "PROCEED")
    watch_count = sum(1 for _, label in top_matches if label == "WATCH")

    if proceed_count > watch_count:
        return {"prediction": "PROCEED"}
    else:
        return {"prediction": "WATCH"}
