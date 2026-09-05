"""
ai_routes.py — Routes for AI reasoning, problem database, simulation, and progress tracking
"""

import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session

from Backend.database import get_db
from Backend.models import Problem, UserProgress, StudentKnowledge, Attempt, User
from Backend.routes.auth_routes import get_optional_user, get_current_user
from AI_engine.services.ai_service import ai_service
from Backend.services.simulation_service import run_simulation

router = APIRouter()


def canonical_problem_id(problem_id: str, db: Session) -> str:
    """Return the public database ID for either kebab- or snake-case input."""
    normalized = problem_id.strip().lower().replace("_", "-")
    problem = db.query(Problem).filter(Problem.id == normalized).first()
    if not problem:
        raise HTTPException(status_code=404, detail=f"Problem '{problem_id}' not found")
    return problem.id


def ai_problem_id(problem_id: str) -> str:
    """ML datasets use snake_case while the public problem API uses kebab-case."""
    return problem_id.strip().lower().replace("-", "_")


# ---------------- REQUEST MODELS ----------------

class UnderstandingReq(BaseModel):
    text: str
    problem_id: str
    problem_description: str | None = ""

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
    problem_description: str | None = ""

class SimulateReq(BaseModel):
    problem_id: str
    code: str | None = ""
    input_data: dict | None = {}
    use_optimal: bool = False

class ProgressSaveReq(BaseModel):
    problem_id: str
    status: str | None = "attempted" # "attempted", "solved"
    whiteboard_content: str | None = ""
    flowchart_data: list | dict | None = []
    concept_breakdown: dict | None = {}


# ---------------- PROBLEM DATABASE ROUTES ----------------

@router.get("/problems")
def list_problems(db: Session = Depends(get_db)):
    problems = db.query(Problem).all()
    res = []
    for p in problems:
        res.append({
            "id": p.id,
            "title": p.title,
            "difficulty": p.difficulty,
            "category": p.category,
            "tags": p.tags,
            "description": p.description[:120] + "..." if len(p.description) > 120 else p.description
        })
    return {"success": True, "problems": res}


@router.get("/problems/{problem_id}")
def get_problem(problem_id: str, db: Session = Depends(get_db)):
    canonical_id = canonical_problem_id(problem_id, db)
    p = db.query(Problem).filter(Problem.id == canonical_id).first()
    
    return {
        "success": True,
        "problem": {
            "id": p.id,
            "title": p.title,
            "difficulty": p.difficulty,
            "category": p.category,
            "tags": p.tags,
            "description": p.description,
            "constraints": p.constraints,
            "examples": p.examples,
            "prompts": p.prompts,
            "starter_input": p.starter_input,
            "solution_code": p.solution_code
        }
    }


class MentorUnderstandReq(BaseModel):
    statement: str | None = ""
    constraints: str | None = ""

class MentorPatternReq(BaseModel):
    user_thoughts: str | None = ""
    code_draft: str | None = ""

class MentorBridgeReq(BaseModel):
    thought: str | None = ""
    code: str | None = ""

class MentorReviewReq(BaseModel):
    code: str
    language: str | None = "python"
    test_results: dict | None = None


# ---------------- 9-STAGE MENTOR PIPELINE ROUTES ----------------

@router.post("/mentor/{problem_id}/understand")
def mentor_understand(problem_id: str, req: MentorUnderstandReq, db: Session = Depends(get_db)):
    canonical_id = canonical_problem_id(problem_id, db)
    problem = db.query(Problem).filter(Problem.id == canonical_id).first()
    title = problem.title if problem else problem_id
    statement = req.statement or (problem.description if problem else "")
    res = ai_service.understand_problem(problem_id=canonical_id, title=title, statement=statement, constraints=req.constraints or "")
    return {"success": True, "result": res}


@router.post("/mentor/{problem_id}/pattern-hint")
def mentor_pattern_hint(problem_id: str, req: MentorPatternReq, db: Session = Depends(get_db)):
    canonical_id = canonical_problem_id(problem_id, db)
    problem = db.query(Problem).filter(Problem.id == canonical_id).first()
    title = problem.title if problem else problem_id
    res = ai_service.pattern_hint(problem_id=canonical_id, title=title, user_thoughts=req.user_thoughts or "", code_draft=req.code_draft or "")
    return {"success": True, "result": res}


@router.post("/mentor/{problem_id}/bridge")
def mentor_bridge(problem_id: str, req: MentorBridgeReq, db: Session = Depends(get_db)):
    canonical_id = canonical_problem_id(problem_id, db)
    problem = db.query(Problem).filter(Problem.id == canonical_id).first()
    title = problem.title if problem else problem_id
    desc = problem.description if problem else ""
    options = ai_service.get_bridge_options(thought=req.thought or "", code=req.code or "", problem_id=canonical_id, problem_title=title, problem_description=desc)
    return {"success": True, "options": options}


@router.post("/mentor/{problem_id}/review")
def mentor_review(problem_id: str, req: MentorReviewReq, db: Session = Depends(get_db)):
    canonical_id = canonical_problem_id(problem_id, db)
    res = ai_service.review_code(problem_id=canonical_id, code=req.code, language=req.language or "python", test_results=req.test_results)
    return {"success": True, "result": res}


# ---------------- ORIGINAL AI REASONING ROUTES ----------------

@router.post("/understanding")
def check_understanding(req: UnderstandingReq):
    try:
        result = ai_service.evaluate_understanding(
            text=req.text,
            problem_id=ai_problem_id(req.problem_id),
            problem_description=req.problem_description or ""
        )
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/hint")
def hint_api(req: HintReq):
    try:
        pid = ai_problem_id(req.problem_id) if req.problem_id else "unknown"
        hints = ai_service.get_progressive_hints(
            problem_id=pid,
            code=req.code or "",
            thinking_state=req.thinking_state or "surface_thinking",
            problem_description=req.problem_description or ""
        )
        # Extract hint text strings for frontend list compatibility
        hint_strings = [h["hint"] for h in hints]
        return {"success": True, "hints": hint_strings, "progressive_hints": hints}
    except Exception as e:
        return {"success": False, "error": str(e), "hints": []}


@router.post("/next-step")
def next_step_api(req: NextStepReq):
    try:
        steps = ai_service.get_next_steps(
            thought=req.thought,
            problem_id=ai_problem_id(req.problem_id),
            thinking_state=req.thinking_state or "surface_thinking",
            problem_description=req.problem_description or ""
        )
        return {"success": True, "next_steps": steps}
    except Exception as e:
        return {"success": False, "error": str(e), "next_steps": []}


@router.post("/evaluate")
def evaluate_code(req: CodeRequest):
    try:
        result = ai_service.evaluate_pseudocode(
            code=req.code,
            problem_description=req.problem_description or ""
        )
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/simulate")
def simulate_algorithm(req: SimulateReq):
    try:
        result = run_simulation(
            problem_id=req.problem_id,
            code=req.code or "",
            input_data=req.input_data or {},
            use_optimal=req.use_optimal,
        )
        if "error" in result:
            return {"success": False, "error": result["error"], "steps": [], "is_graph": False}
        return {"success": True, **result}
    except Exception as e:
        return {"success": False, "error": str(e), "steps": [], "is_graph": False}


# ---------------- PROGRESS & DASHBOARD ROUTES ----------------

@router.post("/progress/save")
def save_progress(
    req: ProgressSaveReq,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        problem_id = canonical_problem_id(req.problem_id, db)
        progress = db.query(UserProgress).filter(
            UserProgress.user_id == current_user.id,
            UserProgress.problem_id == problem_id
        ).first()

        if not progress:
            progress = UserProgress(
                user_id=current_user.id,
                problem_id=problem_id,
                status=req.status or "attempted",
                whiteboard_content=req.whiteboard_content or "",
                flowchart_json=json.dumps(req.flowchart_data or []),
                concept_breakdown_json=json.dumps(req.concept_breakdown or {}),
                attempts_count=1
            )
            db.add(progress)
        else:
            if req.status: progress.status = req.status
            if req.whiteboard_content is not None: progress.whiteboard_content = req.whiteboard_content
            if req.flowchart_data is not None: progress.flowchart_json = json.dumps(req.flowchart_data)
            if req.concept_breakdown is not None: progress.concept_breakdown_json = json.dumps(req.concept_breakdown)
            progress.attempts_count += 1
            progress.last_attempt_at = datetime.utcnow()

        # Update student knowledge stats if solved
        if req.status == "solved":
            knowledge = db.query(StudentKnowledge).filter(StudentKnowledge.user_id == current_user.id).first()
            if knowledge:
                knowledge.solved_count += 1
                knowledge.updated_at = datetime.utcnow()

        db.commit()
        return {"success": True, "message": "Progress saved successfully"}
    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}


@router.get("/progress/{problem_id}")
def get_progress(
    problem_id: str,
    user: User | None = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    if not user:
        return {"success": True, "progress": None}

    canonical_id = canonical_problem_id(problem_id, db)
    
    prog = db.query(UserProgress).filter(
        UserProgress.user_id == user.id,
        UserProgress.problem_id == canonical_id
    ).first()

    if not prog:
        return {"success": True, "progress": None}
    
    return {
        "success": True,
        "progress": {
            "status": prog.status,
            "whiteboard_content": prog.whiteboard_content,
            "flowchart_data": json.loads(prog.flowchart_json or "[]"),
            "concept_breakdown": json.loads(prog.concept_breakdown_json or "{}"),
            "attempts_count": prog.attempts_count,
            "last_attempt_at": prog.last_attempt_at.isoformat()
        }
    }


@router.get("/dashboard")
def get_dashboard(
    user: User | None = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    if not user:
        # Default fallback for unauthenticated preview
        user = db.query(User).filter(User.email == "demo@algomentor.com").first()

    user_id = user.id if user else 1
    knowledge = db.query(StudentKnowledge).filter(StudentKnowledge.user_id == user_id).first()
    solved_ids = [p.problem_id for p in db.query(UserProgress).filter(UserProgress.user_id == user_id, UserProgress.status == "solved").all()]

    weak_topics = json.loads(knowledge.weak_topics_json) if knowledge else ["Graphs", "Dynamic Programming"]
    mastered_topics = json.loads(knowledge.mastered_topics_json) if knowledge else ["Arrays"]

    recs = ai_service.recommend_problems(weak_topics=weak_topics, solved_ids=solved_ids)

    return {
        "success": True,
        "profile": {
            "name": user.name if user else "Alex Chen",
            "email": user.email if user else "demo@algomentor.com",
            "level": user.level if user else "Intermediate",
            "streak": knowledge.streak_days if knowledge else 7,
            "solved_count": len(solved_ids) or (knowledge.solved_count if knowledge else 5),
            "total_problems": db.query(Problem).count() or 10
        },
        "recommendations": recs,
        "skill_progress": [
            {"name": "Arrays", "progress": 80, "problems": 20},
            {"name": "Searching", "progress": 65, "problems": 15},
            {"name": "Sorting", "progress": 85, "problems": 18},
            {"name": "Linked Lists", "progress": 50, "problems": 10},
            {"name": "Stacks & Queues", "progress": 70, "problems": 14},
            {"name": "Graphs", "progress": 40, "problems": 8},
            {"name": "Dynamic Programming", "progress": 35, "problems": 6},
        ]
    }
