"""
understanding_model.py  —  AlgoMentor AI Engine
================================================
Upgraded from TF-IDF + LogisticRegression to a multi-input
sentence-embedding MLP classifier.

Architecture:
  • SentenceTransformer (all-MiniLM-L6-v2) encodes:
      - problem_description  →  384-d embedding
      - user_thought         →  384-d embedding
  • OneHotEncoder encodes problem_id (categorical)
  • Concatenated feature vector → [768 + n_problems] dimensions
  • MLPClassifier (512→256→128) with early stopping

Outputs:
  • thinking_state  : surface_thinking | deep_reasoning | stuck |
                      off_track | optimal_thinking
  • confidence      : float [0, 1]
  • prediction      : PROCEED | WATCH  (backward-compatible)
  • feedback        : human-readable string

Public API (unchanged contract with orchestrator / model_service):
  train_model(dataset_path)  →  dict(accuracy, f1)
  predict(text, problem_id, problem_description)  →  dict
  save_model()
  load_model()
"""

import os
import json
import numpy as np
import joblib

from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, classification_report
from sentence_transformers import SentenceTransformer

# ──────────────────────────────────────────────────────────────
# Paths
# ──────────────────────────────────────────────────────────────
MODEL_DIR = os.path.join("AI_engine", "trained_models", "understanding_model")
os.makedirs(MODEL_DIR, exist_ok=True)

_MLP_PATH   = os.path.join(MODEL_DIR, "model.pkl")
_VEC_PATH   = os.path.join(MODEL_DIR, "vectorizer.pkl")   # kept for path-compat
_LE_PATH    = os.path.join(MODEL_DIR, "label_encoder.pkl")
_PID_PATH   = os.path.join(MODEL_DIR, "pid_encoder.pkl")

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# ──────────────────────────────────────────────────────────────
# Module-level singletons (lazy-loaded)
# ──────────────────────────────────────────────────────────────
_embedder       = None
_mlp            = None
_label_encoder  = None
_pid_encoder    = None

# ──────────────────────────────────────────────────────────────
# Human-readable feedback per thinking state
# ──────────────────────────────────────────────────────────────
_FEEDBACK = {
    "surface_thinking": (
        "You have a surface-level approach. Your logic is correct in direction "
        "but consider the time complexity. Try to think about whether a more "
        "efficient data structure could eliminate redundant work."
    ),
    "deep_reasoning": (
        "You are reasoning deeply about this problem. You have identified the "
        "core trade-off. Keep refining — you are close to an optimal solution."
    ),
    "stuck": (
        "It looks like you are stuck. Try breaking the problem into the smallest "
        "possible sub-question: what single piece of information do you need at "
        "each step? Start from a brute-force observation and work upward."
    ),
    "off_track": (
        "Your current approach does not align well with the problem constraints. "
        "Re-read the problem statement carefully, particularly what the output "
        "must be and what operations are allowed."
    ),
    "optimal_thinking": (
        "Excellent reasoning! Your approach aligns with an optimal strategy. "
        "Focus on edge cases and clean implementation details."
    ),
}


# ──────────────────────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────────────────────
def _get_embedder() -> SentenceTransformer:
    global _embedder
    if _embedder is None:
        print("[UnderstandingModel] Loading SentenceTransformer …")
        _embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _embedder


def _build_features(
    problem_descriptions: list[str],
    user_thoughts:        list[str],
    problem_ids:          list[str],
    fit: bool = False,
) -> np.ndarray:
    """
    Encode inputs into a single concatenated feature matrix.
    fit=True during training (fits the PID encoder).
    fit=False during inference (transforms only).
    """
    global _pid_encoder

    embedder = _get_embedder()

    desc_emb    = embedder.encode(problem_descriptions, batch_size=32,
                                  show_progress_bar=False, normalize_embeddings=True)
    thought_emb = embedder.encode(user_thoughts,        batch_size=32,
                                  show_progress_bar=False, normalize_embeddings=True)

    pid_arr = np.array(problem_ids).reshape(-1, 1)
    if fit:
        _pid_encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
        pid_enc = _pid_encoder.fit_transform(pid_arr)
    else:
        pid_enc = _pid_encoder.transform(pid_arr)

    return np.concatenate([desc_emb, thought_emb, pid_enc], axis=1)


# ──────────────────────────────────────────────────────────────
# TRAIN
# ──────────────────────────────────────────────────────────────
def train_model(dataset_path: str) -> dict:
    """
    Train the MLP understanding classifier.

    Dataset format (each entry):
        {
          "problem_id":          str,
          "problem_description": str,
          "user_thought":        str,
          "thinking_state":      str   ← label
        }

    Returns:
        {"accuracy": float, "f1": float}
    """
    global _mlp, _label_encoder

    print("[UnderstandingModel] Loading dataset …")
    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if len(data) < 5:
        raise ValueError("Dataset too small. Add at least 5 entries.")

    problem_descriptions = [d["problem_description"] for d in data]
    user_thoughts        = [d["user_thought"]        for d in data]
    problem_ids          = [d["problem_id"]           for d in data]
    raw_labels           = [d["thinking_state"]       for d in data]

    _label_encoder = LabelEncoder()
    y = _label_encoder.fit_transform(raw_labels)

    print("[UnderstandingModel] Building feature matrix …")
    X = _build_features(problem_descriptions, user_thoughts, problem_ids, fit=True)

    # Stratified split — fall back to simple split for very small datasets
    try:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
    except ValueError:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

    _mlp = MLPClassifier(
        hidden_layer_sizes=(512, 256, 128),
        activation="relu",
        solver="adam",
        learning_rate_init=1e-3,
        max_iter=500,
        early_stopping=True,
        validation_fraction=0.15,
        n_iter_no_change=25,
        random_state=42,
        verbose=False,
    )

    print("[UnderstandingModel] Training MLP …")
    _mlp.fit(X_train, y_train)

    y_pred = _mlp.predict(X_test)
    acc    = float(accuracy_score(y_test, y_pred))
    f1     = float(f1_score(y_test, y_pred, average="weighted", zero_division=0))

    print(f"[UnderstandingModel] Accuracy: {acc:.4f}  |  F1: {f1:.4f}")
    print(classification_report(
        y_test, y_pred,
        target_names=_label_encoder.classes_,
        zero_division=0,
    ))

    save_model()
    return {"accuracy": acc, "f1": f1}


# ──────────────────────────────────────────────────────────────
# SAVE / LOAD
# ──────────────────────────────────────────────────────────────
def save_model() -> None:
    joblib.dump(_mlp,          _MLP_PATH)
    joblib.dump(_label_encoder, _LE_PATH)
    joblib.dump(_pid_encoder,  _PID_PATH)
    # Write a placeholder vectorizer.pkl so legacy code that checks the old
    # path does not crash (it is unused in the new pipeline).
    joblib.dump({}, _VEC_PATH)
    print("[UnderstandingModel] Saved ✅")


def load_model() -> None:
    global _mlp, _label_encoder, _pid_encoder

    if _mlp is not None:
        return                          # already loaded

    for path, label in [(_MLP_PATH, "model"), (_LE_PATH, "label_encoder"),
                        (_PID_PATH, "pid_encoder")]:
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"[UnderstandingModel] ❌ Missing {label} at {path}. "
                "Run retrain.py first."
            )

    _mlp           = joblib.load(_MLP_PATH)
    _label_encoder = joblib.load(_LE_PATH)
    _pid_encoder   = joblib.load(_PID_PATH)
    print("[UnderstandingModel] Loaded ✅")


# ──────────────────────────────────────────────────────────────
# PREDICT
# ──────────────────────────────────────────────────────────────
def predict(
    text:                str,
    problem_id:          str = "unknown",
    problem_description: str = "",
) -> dict:
    """
    Predict the student's thinking state.

    Args:
        text                : user's pseudocode / thought  (required)
        problem_id          : problem identifier           (optional, improves accuracy)
        problem_description : full problem statement       (optional, improves accuracy)

    Returns:
        {
            "prediction":     "PROCEED" | "WATCH",    ← backward-compatible
            "thinking_state": str,
            "confidence":     float,
            "reason":         str,
            "feedback":       str,
        }
    """
    load_model()

    # Graceful degradation: if no problem_description provided, use text as proxy
    desc = problem_description if problem_description.strip() else text

    X = _build_features([desc], [text], [problem_id], fit=False)

    proba         = _mlp.predict_proba(X)[0]
    pred_idx      = int(np.argmax(proba))
    thinking_state = _label_encoder.inverse_transform([pred_idx])[0]
    confidence    = round(float(proba[pred_idx]), 4)

    proceed_states = {"deep_reasoning", "optimal_thinking"}
    decision       = "PROCEED" if thinking_state in proceed_states else "WATCH"
    feedback       = _FEEDBACK.get(thinking_state, "Keep analysing the problem carefully.")

    return {
        "prediction":     decision,
        "thinking_state": thinking_state,
        "confidence":     confidence,
        "reason":         feedback,
        "feedback":       feedback,
    }


# ──────────────────────────────────────────────────────────────
# CLI entry point
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    train_model("Datasets/understanding_dataset.json")
    result = predict(
        text="I will store numbers in a hashmap and check complement",
        problem_id="two_sum",
        problem_description="Return indices of two numbers that add up to target.",
    )
    print(result)
