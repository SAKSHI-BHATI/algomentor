"""
hint_generation_model.py  —  AlgoMentor AI Engine
==================================================
Upgraded from hardcoded rule-based matching to a
Retrieval-Augmented Generation (RAG) approach using
dense semantic embeddings.

Architecture:
  • All hint entries in the dataset are embedded offline
    using SentenceTransformer (all-MiniLM-L6-v2).
  • At query time, the combined context
    (problem_id + thinking_state + problem_description + user_code)
    is embedded and cosine-similarity ranked against the index.
  • Hints matching problem_id receive a +0.15 boost.
  • Hints matching thinking_state receive a +0.20 boost.
  • Top-K unique hints are returned (K=3 for backward compat).

Dataset format (flat entries — no hint-type buckets):
    {
      "problem_id":       str,
      "thinking_state":   str,
      "problem_context":  str,
      "user_code_snippet": str,
      "hint":             str
    }

Public API:
    build_index(dataset_path)           — call during training
    predict(problem_id, code,           — call during inference
            thinking_state,
            problem_description) → list[str]
"""

import os
import json
import numpy as np
import joblib

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# ──────────────────────────────────────────────────────────────
# Paths
# ──────────────────────────────────────────────────────────────
DATA_PATH  = os.path.join("Datasets", "Hint_Generation_Dataset.json")
MODEL_DIR  = os.path.join("AI_engine", "trained_models", "hint_model")
os.makedirs(MODEL_DIR, exist_ok=True)

_EMBEDDINGS_PATH = os.path.join(MODEL_DIR, "hint_embeddings.pkl")
_ENTRIES_PATH    = os.path.join(MODEL_DIR, "hint_entries.pkl")

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# Retrieval constants
_TOP_K           = 3      # hints returned per query
_PID_BOOST       = 0.15   # score boost for matching problem_id
_STATE_BOOST     = 0.20   # score boost for matching thinking_state
_MIN_FALLBACK    = 0.0    # accept any result (fallback handled explicitly)

# ──────────────────────────────────────────────────────────────
# Singletons
# ──────────────────────────────────────────────────────────────
_embedder        = None
_hint_embeddings = None   # np.ndarray  shape (N, 384)
_hint_entries    = None   # list[dict]

# ──────────────────────────────────────────────────────────────
# Fallback hints when index is empty / no match found
# ──────────────────────────────────────────────────────────────
_FALLBACK_HINTS = [
    "Break the problem into the smallest solvable sub-question first.",
    "Think about what data structure captures the information you need in O(1).",
    "Analyse the time complexity of your current approach before optimising.",
]


# ──────────────────────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────────────────────
def _get_embedder() -> SentenceTransformer:
    global _embedder
    if _embedder is None:
        print("[HintModel] Loading SentenceTransformer …")
        _embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _embedder


def _build_index_string(entry: dict) -> str:
    """
    Create a rich text representation of a hint entry for embedding.
    Including the hint text makes the index searchable by semantic content.
    """
    return (
        f"Problem: {entry.get('problem_id', '')} | "
        f"State: {entry.get('thinking_state', '')} | "
        f"Context: {entry.get('problem_context', '')} | "
        f"Code: {entry.get('user_code_snippet', '')} | "
        f"Hint: {entry.get('hint', '')}"
    )


def _build_query_string(
    problem_id:          str,
    code:                str,
    thinking_state:      str,
    problem_description: str,
) -> str:
    return (
        f"Problem: {problem_id} | "
        f"State: {thinking_state} | "
        f"Context: {problem_description} | "
        f"Code: {code}"
    )


# ──────────────────────────────────────────────────────────────
# BUILD INDEX  (training / indexing phase)
# ──────────────────────────────────────────────────────────────
def build_index(dataset_path: str = DATA_PATH) -> None:
    """
    Embed all hint entries and persist the index to disk.
    Must be called once before inference.
    """
    global _hint_embeddings, _hint_entries

    print(f"[HintModel] Loading dataset from {dataset_path} …")
    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not data:
        raise ValueError("[HintModel] Dataset is empty.")

    _hint_entries = data
    embedder = _get_embedder()

    index_strings = [_build_index_string(e) for e in data]
    print(f"[HintModel] Embedding {len(index_strings)} hint entries …")
    _hint_embeddings = embedder.encode(
        index_strings,
        batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True,
    )

    joblib.dump(_hint_embeddings, _EMBEDDINGS_PATH)
    joblib.dump(_hint_entries,    _ENTRIES_PATH)
    print(f"[HintModel] Index built: {len(_hint_entries)} entries ✅")


# ──────────────────────────────────────────────────────────────
# LOAD INDEX  (lazy on first predict call)
# ──────────────────────────────────────────────────────────────
def _load_index() -> None:
    global _hint_embeddings, _hint_entries

    if _hint_embeddings is not None:
        return

    for path, label in [(_EMBEDDINGS_PATH, "hint_embeddings"),
                        (_ENTRIES_PATH,    "hint_entries")]:
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"[HintModel] ❌ Missing {label} at {path}. "
                "Run retrain.py first."
            )

    _hint_embeddings = joblib.load(_EMBEDDINGS_PATH)
    _hint_entries    = joblib.load(_ENTRIES_PATH)
    print("[HintModel] Index loaded ✅")


# ──────────────────────────────────────────────────────────────
# PREDICT
# ──────────────────────────────────────────────────────────────
def predict(
    problem_id:          str  = None,
    code:                str  = "",
    thinking_state:      str  = "surface_thinking",
    problem_description: str  = "",
) -> list[str]:
    """
    Retrieve the top-K most contextually appropriate hints.

    Args:
        problem_id          : problem identifier (e.g. "two_sum")
        code                : student's current pseudocode / code snippet
        thinking_state      : output from understanding_model
        problem_description : full problem statement text

    Returns:
        list[str]  — up to 3 hint strings, ranked by relevance
    """
    _load_index()
    embedder = _get_embedder()

    pid   = problem_id or "unknown"
    query = _build_query_string(pid, code, thinking_state, problem_description)

    q_emb = embedder.encode(
        [query],
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    # Base cosine similarity
    raw_sims = cosine_similarity(q_emb, _hint_embeddings)[0]

    # Apply contextual boosts (soft filtering — never hard-exclude)
    boosted_sims = raw_sims.copy()
    for i, entry in enumerate(_hint_entries):
        if entry.get("problem_id") == pid:
            boosted_sims[i] += _PID_BOOST
        if entry.get("thinking_state") == thinking_state:
            boosted_sims[i] += _STATE_BOOST

    # Rank and deduplicate
    ranked_indices = np.argsort(boosted_sims)[::-1]

    hints       = []
    seen_texts  = set()
    for idx in ranked_indices:
        hint_text = _hint_entries[idx]["hint"].strip()
        if hint_text and hint_text not in seen_texts:
            hints.append(hint_text)
            seen_texts.add(hint_text)
        if len(hints) == _TOP_K:
            break

    return hints if hints else _FALLBACK_HINTS[:]


# ──────────────────────────────────────────────────────────────
# CLI entry point
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    build_index(DATA_PATH)
    result = predict(
        problem_id="two_sum",
        code="for i in range(n): for j in range(i+1,n):",
        thinking_state="surface_thinking",
        problem_description="Return indices of two numbers that add up to target.",
    )
    for i, h in enumerate(result, 1):
        print(f"Hint {i}: {h}")
