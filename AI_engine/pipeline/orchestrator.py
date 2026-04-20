"""
orchestrator.py  —  AlgoMentor AI Engine
=========================================
Central pipeline runner.  Supports individual stages AND a
"full" stage that chains understanding → hints + next_steps
automatically, passing thinking_state between models.

Backward-compatible:  existing callers that use
    run_pipeline("understanding", {"text": ...})
    run_pipeline("hint",          {"problem_id": ..., "code": ...})
    run_pipeline("next_step",     {"thought": ...})
    run_pipeline("evaluate",      {"code": ...})
continue to work unchanged.

New:
    run_pipeline("full", {
        "text":                str,   # student's thought / pseudocode
        "problem_id":          str,
        "problem_description": str,
        "code":                str,   # optional — defaults to text
    })
    → {
        "understanding": {...},
        "hints":         [...],
        "next_steps":    [...],
      }
"""

from AI_engine.model_logic.understanding_model      import predict as _understanding
from AI_engine.model_logic.hint_generation_model    import predict as _hint
from AI_engine.model_logic.reasoning_next_step_model import predict as _next_step
from AI_engine.model_logic.pseudocode_evaluation_model import predict as _evaluate


def run_pipeline(stage: str, data: dict) -> dict | list | str:
    """
    Dispatch to the appropriate model(s).

    Args:
        stage : "understanding" | "hint" | "next_step" | "evaluate" | "full"
        data  : dict of inputs (see per-stage notes above)

    Returns:
        Model output — type depends on stage.
        On error returns {"error": str}.
    """
    try:
        # ── Understanding ──────────────────────────────────────────────
        if stage == "understanding":
            return _understanding(
                text                = data.get("text", ""),
                problem_id          = data.get("problem_id", "unknown"),
                problem_description = data.get("problem_description", ""),
            )

        # ── Hint  ──────────────────────────────────────────────────────
        elif stage == "hint":
            return _hint(
                problem_id          = data.get("problem_id"),
                code                = data.get("code", ""),
                thinking_state      = data.get("thinking_state", "surface_thinking"),
                problem_description = data.get("problem_description", ""),
            )

        # ── Next step  ─────────────────────────────────────────────────
        elif stage == "next_step":
            return _next_step(
                user_input          = data.get("thought", ""),
                problem_id          = data.get("problem_id", "unknown"),
                thinking_state      = data.get("thinking_state", "surface_thinking"),
                problem_description = data.get("problem_description", ""),
            )

        # ── Evaluate (pseudocode_evaluation_model — unchanged) ─────────
        elif stage == "evaluate":
            return _evaluate(data.get("code", ""))

        # ── Full chained pipeline ──────────────────────────────────────
        elif stage == "full":
            text                = data.get("text", "")
            problem_id          = data.get("problem_id", "unknown")
            problem_description = data.get("problem_description", "")
            code                = data.get("code", text)

            # Step 1: classify student's thinking state
            understanding_result = _understanding(
                text                = text,
                problem_id          = problem_id,
                problem_description = problem_description,
            )

            # Propagate thinking_state downstream
            thinking_state = understanding_result.get("thinking_state", "surface_thinking")

            # Step 2: retrieve adaptive hints conditioned on thinking_state
            hint_result = _hint(
                problem_id          = problem_id,
                code                = code,
                thinking_state      = thinking_state,
                problem_description = problem_description,
            )

            # Step 3: retrieve next steps conditioned on thinking_state
            next_step_result = _next_step(
                user_input          = text,
                problem_id          = problem_id,
                thinking_state      = thinking_state,
                problem_description = problem_description,
            )

            return {
                "understanding": understanding_result,
                "hints":         hint_result,
                "next_steps":    next_step_result,
            }

        else:
            return {"error": f"Invalid stage '{stage}'. "
                             "Valid stages: understanding, hint, next_step, evaluate, full"}

    except FileNotFoundError as e:
        # Model not yet trained — surface a clear message
        return {"error": str(e)}

    except Exception as e:
        return {"error": str(e)}
