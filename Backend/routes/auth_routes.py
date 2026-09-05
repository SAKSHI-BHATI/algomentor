"""
auth_routes.py — User Registration, Login, and JWT Session management
"""

import os
import hmac
import hashlib
import json
import base64
import time
from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from Backend.database import get_db
from Backend.models import User, StudentKnowledge

router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "algomentor_super_secret_jwt_key_2026")


# ── Password & Token Helpers ──────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return hashlib.sha256((password + SECRET_KEY).encode("utf-8")).hexdigest()


def create_access_token(data: dict, expires_delta: int = 86400 * 7) -> str:
    payload = data.copy()
    payload["exp"] = int(time.time()) + expires_delta
    payload_bytes = json.dumps(payload).encode("utf-8")
    payload_b64 = base64.urlsafe_b64encode(payload_bytes).decode("utf-8").rstrip("=")
    
    signature = hmac.new(SECRET_KEY.encode("utf-8"), payload_b64.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{payload_b64}.{signature}"


def verify_access_token(token: str) -> dict | None:
    try:
        parts = token.split(".")
        if len(parts) != 2:
            return None
        payload_b64, signature = parts
        expected_sig = hmac.new(SECRET_KEY.encode("utf-8"), payload_b64.encode("utf-8"), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected_sig):
            return None
        
        # Add padding back if necessary
        padding = "=" * (4 - len(payload_b64) % 4)
        payload_bytes = base64.urlsafe_b64decode(payload_b64 + padding)
        payload = json.loads(payload_bytes.decode("utf-8"))
        
        if payload.get("exp", 0) < time.time():
            return None
        return payload
    except Exception:
        return None


def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)) -> User:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    token = authorization.replace("Bearer ", "").strip()
    payload = verify_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user = db.query(User).filter(User.id == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def get_optional_user(authorization: str = Header(None), db: Session = Depends(get_db)) -> User | None:
    if not authorization:
        return None
    try:
        token = authorization.replace("Bearer ", "").strip()
        payload = verify_access_token(token)
        if not payload or "sub" not in payload:
            return None
        return db.query(User).filter(User.id == payload["sub"]).first()
    except Exception:
        return None


# ── Schemas ───────────────────────────────────────────────────────────────────

class RegisterReq(BaseModel):
    email: str
    password: str
    name: str | None = "Student"


class LoginReq(BaseModel):
    email: str
    password: str


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/register")
def register(req: RegisterReq, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == req.email.lower().strip()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = User(
        email=req.email.lower().strip(),
        name=req.name or "Student",
        password_hash=hash_password(req.password),
        level="Intermediate"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Initialize Knowledge State
    knowledge = StudentKnowledge(
        user_id=user.id,
        mastered_topics_json=json.dumps([]),
        weak_topics_json=json.dumps(["Arrays", "Graphs", "Dynamic Programming"]),
        streak_days=1,
        solved_count=0
    )
    db.add(knowledge)
    db.commit()

    token = create_access_token({"sub": user.id, "email": user.email})
    return {
        "success": True,
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "level": user.level,
            "streak": 1,
            "solved_count": 0
        }
    }


@router.post("/login")
def login(req: LoginReq, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email.lower().strip()).first()
    if not user or user.password_hash != hash_password(req.password):
        # Demo login fallback for convenience
        if req.email == "demo@algomentor.com":
            user = db.query(User).filter(User.email == "demo@algomentor.com").first()
            if not user:
                user = User(
                    email="demo@algomentor.com",
                    name="Alex Chen",
                    password_hash=hash_password("demo123"),
                    level="Intermediate"
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                knowledge = StudentKnowledge(user_id=user.id, streak_days=7, solved_count=5)
                db.add(knowledge)
                db.commit()
        else:
            raise HTTPException(status_code=400, detail="Invalid email or password")

    token = create_access_token({"sub": user.id, "email": user.email})
    knowledge = db.query(StudentKnowledge).filter(StudentKnowledge.user_id == user.id).first()

    return {
        "success": True,
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "level": user.level,
            "streak": knowledge.streak_days if knowledge else 1,
            "solved_count": knowledge.solved_count if knowledge else 0
        }
    }


@router.get("/me")
def me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    knowledge = db.query(StudentKnowledge).filter(StudentKnowledge.user_id == current_user.id).first()
    return {
        "success": True,
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "name": current_user.name,
            "level": current_user.level,
            "streak": knowledge.streak_days if knowledge else 1,
            "solved_count": knowledge.solved_count if knowledge else 0,
            "mastered_topics": json.loads(knowledge.mastered_topics_json) if knowledge else [],
            "weak_topics": json.loads(knowledge.weak_topics_json) if knowledge else []
        }
    }
