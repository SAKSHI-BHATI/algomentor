"""
execute_routes.py — Code Execution Endpoint for AlgoMentor
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any

from Backend.database import get_db
from Backend.models import Problem, Attempt, User
from Backend.services.executor import execute_code
from Backend.routes.auth_routes import get_optional_user

router = APIRouter(prefix="/api/execute", tags=["Execution"])


class ExecuteRequest(BaseModel):
    code: str
    language: Optional[str] = "python"


@router.post("/{problem_id}")
def run_solution_code(
    problem_id: str,
    req: ExecuteRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Execute user submission against private test cases in database.
    """
    # Canonical ID handling
    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not problem:
        # Try snake_case or hyphenated fallback
        alt_id = problem_id.replace("_", "-") if "_" in problem_id else problem_id.replace("-", "_")
        problem = db.query(Problem).filter(Problem.id == alt_id).first()

    if not problem:
        raise HTTPException(status_code=404, detail=f"Problem '{problem_id}' not found.")

    test_cases = problem.test_cases
    entry_function = problem.entry_function or "solution"

    execution_result = execute_code(
        code=req.code,
        language=req.language or "python",
        test_cases=test_cases,
        entry_function=entry_function,
        timeout=2.5
    )

    # If user is authenticated, record attempt in DB
    if current_user:
        user_id = current_user.id
        try:
            attempt = Attempt(
                user_id=user_id,
                problem_id=problem.id,
                code=req.code,
                thinking_state="coding",
                feedback_json=str(execution_result.get("all_passed", False)),
                understanding_level="PASS" if execution_result.get("all_passed") else "RETRY"
            )
            db.add(attempt)
            db.commit()
        except Exception:
            db.rollback()

    return execution_result
