"""
reasoning_next_step_model.py  —  AlgoMentor AI Engine
======================================================
Upgraded from word-overlap similarity to dense semantic
retrieval with contextual re-ranking.

Architecture:
  • All (input → next_steps) pairs are embedded offline using
    SentenceTransformer (all-MiniLM-L6-v2).
  • The input embedding encodes:
      problem_id + thinking_state + user_pseudocode
  • At query time the joint query is embedded and ranked via
    cosine similarity.
  • problem_id match  → +0.20 boost
  • thinking_state match → +0.15 boost
  • Diversity re-ranking: chosen steps cannot share the first
    60 characters, ensuring variety across the 3 returned steps.

Dataset format:
    {
      "problem_id":          str,
      "problem_description": str,
      "user_pseudocode":     str,
      "thinking_state":      str,
      "next_steps":          list[str]   ← exactly 3 items
    }

Public API:
    build_index(dataset_path)                       — training phase
    predict(user_input, problem_id,                 — inference
            thinking_state, problem_description)
            → list[str]   (exactly 3 next steps)
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
DATA_PATH  = os.path.join("Datasets", "Reasoning_Next_Step_Dataset.json")
MODEL_DIR  = os.path.join("AI_engine", "trained_models", "next_step_model")
os.makedirs(MODEL_DIR, exist_ok=True)

_EMBEDDINGS_PATH = os.path.join(MODEL_DIR, "step_embeddings.pkl")
_ENTRIES_PATH    = os.path.join(MODEL_DIR, "step_entries.pkl")

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# Retrieval constants
_NUM_STEPS     = 3       # always return exactly 3 next steps
_PID_BOOST     = 0.20
_STATE_BOOST   = 0.15
_DIVERSITY_LEN = 60      # de-dup prefix length to ensure step variety

# ──────────────────────────────────────────────────────────────
# Singletons
# ──────────────────────────────────────────────────────────────
_embedder       = None
_step_embeddings = None   # np.ndarray  shape (N, 384)
_step_entries    = None   # list[dict]

# ──────────────────────────────────────────────────────────────
# Generic fallback next steps
# ──────────────────────────────────────────────────────────────
_FALLBACK_STEPS = [
    "Break the problem into the smallest possible sub-question and solve that first.",
    "Identify the data structure that allows constant-time access to the information you need most often.",
    "Analyse your current approach's time complexity and determine whether it meets the problem constraints.",
]


# ──────────────────────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────────────────────
def _get_embedder() -> SentenceTransformer:
    global _embedder
    if _embedder is None:
        print("[NextStepModel] Loading SentenceTransformer …")
        _embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _embedder


def _build_index_string(entry: dict) -> str:
    """
    Encode the *input* side of a dataset entry so that similar
    student states cluster together in embedding space.
    """
    return (
        f"Problem: {entry.get('problem_id', '')} | "
        f"State: {entry.get('thinking_state', '')} | "
        f"Pseudocode: {entry.get('user_pseudocode', '')} | "
        f"Description: {entry.get('problem_description', '')}"
    )


def _build_query_string(
    user_input:          str,
    problem_id:          str,
    thinking_state:      str,
    problem_description: str,
) -> str:
    return (
        f"Problem: {problem_id} | "
        f"State: {thinking_state} | "
        f"Pseudocode: {user_input} | "
        f"Description: {problem_description}"
    )


def _diversify_steps(candidate_entries: list[dict]) -> list[str]:
    """
    Walk ranked entries and collect the first _NUM_STEPS unique step-lists
    whose first steps are sufficiently distinct (diversity by prefix).
    Returns a flat list of exactly _NUM_STEPS step strings.
    """
    collected: list[str] = []
    seen_prefixes: set[str] = set()

    for entry in candidate_entries:
        steps = entry.get("next_steps", [])
        if not steps:
            continue
        prefix = steps[0][:_DIVERSITY_LEN].strip().lower()
        if prefix in seen_prefixes:
            continue
        seen_prefixes.add(prefix)
        collected.extend(steps[:_NUM_STEPS])   # at most 3 from each entry
        if len(collected) >= _NUM_STEPS:
            break

    return collected[:_NUM_STEPS]


# ──────────────────────────────────────────────────────────────
# BUILD INDEX  (training / indexing phase)
# ──────────────────────────────────────────────────────────────
def build_index(dataset_path: str = DATA_PATH) -> None:
    """
    Embed all dataset entries and persist to disk.
    Called once during the training/retraining pipeline.
    """
    global _step_embeddings, _step_entries

    print(f"[NextStepModel] Loading dataset from {dataset_path} …")
    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not data:
        raise ValueError("[NextStepModel] Dataset is empty.")

    _step_entries = data
    embedder = _get_embedder()

    index_strings = [_build_index_string(e) for e in data]
    print(f"[NextStepModel] Embedding {len(index_strings)} entries …")
    _step_embeddings = embedder.encode(
        index_strings,
        batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True,
    )

    joblib.dump(_step_embeddings, _EMBEDDINGS_PATH)
    joblib.dump(_step_entries,    _ENTRIES_PATH)
    print(f"[NextStepModel] Index built: {len(_step_entries)} entries ✅")


# ──────────────────────────────────────────────────────────────
# LOAD INDEX
# ──────────────────────────────────────────────────────────────
def _load_index() -> None:
    global _step_embeddings, _step_entries

    if _step_embeddings is not None:
        return

    for path, label in [(_EMBEDDINGS_PATH, "step_embeddings"),
                        (_ENTRIES_PATH,    "step_entries")]:
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"[NextStepModel] ❌ Missing {label} at {path}. "
                "Run retrain.py first."
            )

    _step_embeddings = joblib.load(_EMBEDDINGS_PATH)
    _step_entries    = joblib.load(_ENTRIES_PATH)
    print("[NextStepModel] Index loaded ✅")


# ──────────────────────────────────────────────────────────────
# PREDICT
# ──────────────────────────────────────────────────────────────
def predict(
    user_input:          str,
    problem_id:          str = "unknown",
    thinking_state:      str = "surface_thinking",
    problem_description: str = "",
) -> list[str]:
    """
    Return exactly 3 logically progressive next steps for the student.

    Args:
        user_input          : student's pseudocode / thought
        problem_id          : problem identifier (improves ranking)
        thinking_state      : from understanding_model (improves ranking)
        problem_description : full problem statement (improves ranking)

    Returns:
        list[str]  — exactly 3 next-step strings
    """
    _load_index()
    embedder = _get_embedder()

    query = _build_query_string(
        user_input, problem_id, thinking_state, problem_description
    )
    q_emb = embedder.encode(
        [query],
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    raw_sims     = cosine_similarity(q_emb, _step_embeddings)[0]
    boosted_sims = raw_sims.copy()

    for i, entry in enumerate(_step_entries):
        if entry.get("problem_id") == problem_id:
            boosted_sims[i] += _PID_BOOST
        if entry.get("thinking_state") == thinking_state:
            boosted_sims[i] += _STATE_BOOST

    ranked_indices  = np.argsort(boosted_sims)[::-1]
    ranked_entries  = [_step_entries[i] for i in ranked_indices]

    steps = _diversify_steps(ranked_entries)

    if len(steps) < _NUM_STEPS:
        # Pad with fallback generic steps if dataset is small
        for fb in _FALLBACK_STEPS:
            if len(steps) >= _NUM_STEPS:
                break
            if fb not in steps:
                steps.append(fb)

    return steps[:_NUM_STEPS]


# ──────────────────────────────────────────────────────────────
# CLI entry point
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    build_index(DATA_PATH)
    steps = predict(
        user_input="I will try all pairs using two loops",
        problem_id="two_sum",
        thinking_state="surface_thinking",
        problem_description="Return indices of two numbers that add up to target.",
    )
    for i, s in enumerate(steps, 1):
        print(f"Step {i}: {s}")
