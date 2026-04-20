from fastapi import APIRouter
from pydantic import BaseModel
from AI_engine.pipeline.orchestrator import run_pipeline
from Backend.services.model_service import model_service

# ── NEW IMPORT (only addition) ─────────────────────────────────────────────────
from Backend.services.simulation_service import run_simulation

router = APIRouter()

# ---------------- REQUEST MODELS ----------------

class UnderstandingReq(BaseModel):
    text: str
    problem_id: str
    problem_description: str

class HintReq(BaseModel):
    problem_id: str | None = None
    problem: str | None = None
    code: str | None = ""
    thinking_state: str | None = "surface_thinking"
    problem_description: str | None = ""

class NextStepReq(BaseModel):
    problem_id: str
    thought: str
    thinking_state: str | None = "surface_thinking"
    problem_description: str | None = ""

class CodeRequest(BaseModel):
    code: str

# ── NEW REQUEST MODEL (only addition) ─────────────────────────────────────────
class SimulateReq(BaseModel):
    problem_id: str
    code: str | None = ""
    input_data: dict | None = {}
    use_optimal: bool = False

# ---------------- ROUTES ----------------

@router.post("/understanding")
def check_understanding(req: UnderstandingReq):
    result = run_pipeline("understanding", {
        "text": req.text,
        "problem_id": req.problem_id,
        "problem_description": req.problem_description
    })

    return {
        "success": True,
        "result": result
    }

@router.post("/hint")
def hint_api(req: HintReq):

    problem_id = req.problem_id

    # fallback mapping (KEEPED)
    if not problem_id and req.problem:
        text = req.problem.lower()

        if "two sum" in text:
            problem_id = "two_sum"
        elif "parentheses" in text:
            problem_id = "valid_parentheses"
        elif "substring" in text:
            problem_id = "longest_substring"

    if not problem_id:
        return {"success": False, "error": "Problem not identified"}

    result = run_pipeline("hint", {
        "problem_id": problem_id,
        "code": req.code or "",
        "thinking_state": req.thinking_state,
        "problem_description": req.problem_description
    })

    return {"success": True, "hints": result}

@router.post("/next-step")
def next_step_api(req: NextStepReq):
    result = run_pipeline("next_step", {
        "problem_id": req.problem_id,
        "thought": req.thought,
        "thinking_state": req.thinking_state,
        "problem_description": req.problem_description
    })

    return {"success": True, "next_steps": result}

@router.post("/evaluate")
def evaluate_code(req: CodeRequest):
    result = model_service.evaluate_pseudocode(req.code)
    return {
        "success": True,
        "result": result
    }

# ── NEW ROUTE (only addition) ──────────────────────────────────────────────────
@router.post("/simulate")
def simulate_algorithm(req: SimulateReq):
    """
    Run a step-by-step simulation for a given problem_id.
    If problem_id == "custom", traces req.code with sys.settrace.
    If use_optimal == True, runs the known-optimal generator.

    Response:
        {
            "success": bool,
            "steps": [
                {
                    "state":     list,
                    "idx1":      int,
                    "idx2":      int,
                    "message":   str,
                    "is_action": bool,
                    "is_graph":  bool,
                    # graph steps also carry:
                    "current_node": int | str,
                    "frontier":     list,
                    "visited":      list,
                }
            ],
            "is_graph": bool
        }
    """
    result = run_simulation(
        problem_id  = req.problem_id,
        code        = req.code or "",
        input_data  = req.input_data or {},
        use_optimal = req.use_optimal,
    )

    if "error" in result:
        return {"success": False, "error": result["error"], "steps": [], "is_graph": False}

    return {"success": True, **result}
