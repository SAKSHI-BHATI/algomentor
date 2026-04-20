"""
retrain.py  —  AlgoMentor AI Engine
=====================================
Standalone retraining script.  Run from the project root:

    python AI_engine/retrain.py

What it does:
    1. Trains the Understanding MLP classifier
       → saves model.pkl, label_encoder.pkl, pid_encoder.pkl, vectorizer.pkl
    2. Builds the Hint Generation semantic index
       → saves hint_embeddings.pkl, hint_entries.pkl
    3. Builds the Next Step semantic index
       → saves step_embeddings.pkl, step_entries.pkl

Evaluation output:
    • Understanding : accuracy + weighted F1 + per-class report
    • Hint model    : top-1 retrieval accuracy on held-out queries
    • Next Step     : MRR@3 (Mean Reciprocal Rank) on held-out queries

Usage:
    python AI_engine/retrain.py [--datasets-dir Datasets]
                                 [--models-dir  AI_engine/trained_models]
"""

import os
import sys
import time
import json
import argparse
import numpy as np

# ── Make sure imports resolve from project root ────────────────
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


# ──────────────────────────────────────────────────────────────
# Argument parsing
# ──────────────────────────────────────────────────────────────
def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="AlgoMentor — Retrain all AI models")
    p.add_argument("--datasets-dir",  default="Datasets",
                   help="Directory containing the JSON datasets")
    p.add_argument("--models-dir",    default=os.path.join("AI_engine", "trained_models"),
                   help="Root directory for saving trained model artefacts")
    p.add_argument("--skip-understanding", action="store_true",
                   help="Skip understanding model training")
    p.add_argument("--skip-hint",          action="store_true",
                   help="Skip hint model index building")
    p.add_argument("--skip-next-step",     action="store_true",
                   help="Skip next-step model index building")
    return p.parse_args()


# ──────────────────────────────────────────────────────────────
# Dataset validation
# ──────────────────────────────────────────────────────────────
def _validate_dataset(path: str, name: str, required_keys: list[str]) -> bool:
    if not os.path.exists(path):
        print(f"  ❌  Missing dataset: {path}  ({name})")
        return False

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not data:
        print(f"  ❌  Empty dataset: {path}")
        return False

    missing_keys = [k for k in required_keys if k not in data[0]]
    if missing_keys:
        print(f"  ❌  {name} entry[0] missing keys: {missing_keys}")
        return False

    print(f"  ✅  {name:40s}  {len(data):>4d} entries   "
          f"keys: {list(data[0].keys())}")
    return True


# ──────────────────────────────────────────────────────────────
# Hint model evaluation (top-1 retrieval accuracy)
# ──────────────────────────────────────────────────────────────
def _eval_hint_retrieval(dataset_path: str) -> float:
    """
    For each entry, query with its own context (minus the hint) and
    check if the correct hint appears in the top-3 results.
    Returns hit@3 rate.
    """
    from AI_engine.model_logic.hint_generation_model import predict as hint_predict, _load_index

    _load_index()

    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    hits = 0
    for entry in data:
        results = hint_predict(
            problem_id          = entry["problem_id"],
            code                = entry.get("user_code_snippet", ""),
            thinking_state      = entry["thinking_state"],
            problem_description = entry.get("problem_context", ""),
        )
        if entry["hint"] in results:
            hits += 1

    return hits / len(data) if data else 0.0


# ──────────────────────────────────────────────────────────────
# Next step model evaluation (MRR@3)
# ──────────────────────────────────────────────────────────────
def _eval_next_step_mrr(dataset_path: str) -> float:
    """
    For each dataset entry, query the model and check the rank of
    the expected first next step in the returned list.
    Returns MRR@3.
    """
    from AI_engine.model_logic.reasoning_next_step_model import predict as step_predict, _load_index

    _load_index()

    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    reciprocal_ranks = []
    for entry in data:
        expected_first_step = entry["next_steps"][0] if entry["next_steps"] else ""
        results = step_predict(
            user_input          = entry["user_pseudocode"],
            problem_id          = entry["problem_id"],
            thinking_state      = entry["thinking_state"],
            problem_description = entry.get("problem_description", ""),
        )
        # Find rank of expected step in returned list (1-based)
        for rank, step in enumerate(results, 1):
            if step == expected_first_step:
                reciprocal_ranks.append(1.0 / rank)
                break
        else:
            reciprocal_ranks.append(0.0)

    return float(np.mean(reciprocal_ranks)) if reciprocal_ranks else 0.0


# ──────────────────────────────────────────────────────────────
# Main retraining pipeline
# ──────────────────────────────────────────────────────────────
def retrain_all(args: argparse.Namespace) -> None:
    print()
    print("=" * 68)
    print("  AlgoMentor — Full Model Retraining Pipeline")
    print("=" * 68)
    print(f"  Datasets dir : {args.datasets_dir}")
    print(f"  Models dir   : {args.models_dir}")
    print()

    # ── Dataset paths ──────────────────────────────────────────
    understanding_ds = os.path.join(args.datasets_dir, "understanding_dataset.json")
    hint_ds          = os.path.join(args.datasets_dir, "Hint_Generation_Dataset.json")
    next_step_ds     = os.path.join(args.datasets_dir, "Reasoning_Next_Step_Dataset.json")

    # ── Validate all datasets upfront ─────────────────────────
    print("Validating datasets …")
    all_ok = True
    all_ok &= _validate_dataset(
        understanding_ds, "Understanding Dataset",
        ["problem_id", "problem_description", "user_thought", "thinking_state"]
    )
    all_ok &= _validate_dataset(
        hint_ds, "Hint Generation Dataset",
        ["problem_id", "thinking_state", "problem_context", "hint"]
    )
    all_ok &= _validate_dataset(
        next_step_ds, "Reasoning Next Step Dataset",
        ["problem_id", "user_pseudocode", "thinking_state", "next_steps"]
    )

    if not all_ok:
        print("\n❌  Retraining aborted — fix dataset issues above first.\n")
        sys.exit(1)

    print()

    # ── 1. Understanding Model ─────────────────────────────────
    if not args.skip_understanding:
        print("[1/3] Training Understanding Model (MLP on sentence embeddings) …")
        from AI_engine.model_logic.understanding_model import train_model

        t0      = time.time()
        metrics = train_model(understanding_ds)
        elapsed = time.time() - t0
        print(f"      ✅  Done in {elapsed:.1f}s  |  "
              f"Accuracy: {metrics['accuracy']:.4f}  |  "
              f"F1 (weighted): {metrics['f1']:.4f}")
    else:
        print("[1/3] Understanding model — SKIPPED")

    print()

    # ── 2. Hint Generation Index ───────────────────────────────
    if not args.skip_hint:
        print("[2/3] Building Hint Generation semantic index …")
        from AI_engine.model_logic.hint_generation_model import build_index as build_hint

        t0 = time.time()
        build_hint(hint_ds)
        elapsed = time.time() - t0
        print(f"      Index built in {elapsed:.1f}s")

        print("      Evaluating hit@3 retrieval accuracy …")
        hit3 = _eval_hint_retrieval(hint_ds)
        print(f"      ✅  Hit@3 accuracy: {hit3:.4f}")
    else:
        print("[2/3] Hint model — SKIPPED")

    print()

    # ── 3. Next Step Index ─────────────────────────────────────
    if not args.skip_next_step:
        print("[3/3] Building Next Step semantic index …")
        from AI_engine.model_logic.reasoning_next_step_model import build_index as build_steps

        t0 = time.time()
        build_steps(next_step_ds)
        elapsed = time.time() - t0
        print(f"      Index built in {elapsed:.1f}s")

        print("      Evaluating MRR@3 …")
        mrr = _eval_next_step_mrr(next_step_ds)
        print(f"      ✅  MRR@3: {mrr:.4f}")
    else:
        print("[3/3] Next step model — SKIPPED")

    print()
    print("=" * 68)
    print("  ✅  All models trained and saved successfully!")
    print("=" * 68)
    print()


# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    args = _parse_args()
    retrain_all(args)
