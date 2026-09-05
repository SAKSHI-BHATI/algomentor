"""
models.py — SQLAlchemy models for AlgoMentor database
"""

import json
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from Backend.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    level = Column(String, default="Intermediate")
    created_at = Column(DateTime, default=datetime.utcnow)

    progress_entries = relationship("UserProgress", back_populates="user", cascade="all, delete-orphan")
    attempts = relationship("Attempt", back_populates="user", cascade="all, delete-orphan")
    knowledge = relationship("StudentKnowledge", back_populates="user", uselist=False, cascade="all, delete-orphan")


class Problem(Base):
    __tablename__ = "problems"

    id = Column(String, primary_key=True, index=True)  # e.g. "two-sum"
    title = Column(String, nullable=False)
    difficulty = Column(String, nullable=False)  # Easy, Medium, Hard
    category = Column(String, nullable=False)    # Arrays, Strings, Sorting, etc.
    pattern = Column(String, default="General")  # Two Pointers, Sliding Window, etc.
    description = Column(Text, nullable=False)
    tags_json = Column(Text, default="[]")        # JSON list
    constraints_json = Column(Text, default="[]") # JSON list
    examples_json = Column(Text, default="[]")    # JSON list of dicts
    prompts_json = Column(Text, default="[]")     # Cognitive prompts
    starter_input_json = Column(Text, default="{}") # Default simulation input dict
    starter_code_json = Column(Text, default="{}")  # {python, javascript, cpp, java}
    entry_function = Column(String, default="solution")
    test_cases_json = Column(Text, default="[]")  # PRIVATE - never sent to frontend!
    solution_code = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    @property
    def tags(self):
        return json.loads(self.tags_json or "[]")

    @property
    def constraints(self):
        return json.loads(self.constraints_json or "[]")

    @property
    def examples(self):
        return json.loads(self.examples_json or "[]")

    @property
    def prompts(self):
        return json.loads(self.prompts_json or "[]")

    @property
    def starter_input(self):
        return json.loads(self.starter_input_json or "{}")

    @property
    def starter_code(self):
        return json.loads(self.starter_code_json or "{}")

    @property
    def test_cases(self):
        return json.loads(self.test_cases_json or "[]")

    def to_dict(self, include_private: bool = False) -> dict:
        data = {
            "id": self.id,
            "title": self.title,
            "difficulty": self.difficulty,
            "category": self.category,
            "pattern": self.pattern,
            "description": self.description,
            "tags": self.tags,
            "constraints": self.constraints,
            "examples": self.examples,
            "prompts": self.prompts,
            "starter_input": self.starter_input,
            "starter_code": self.starter_code,
            "entry_function": self.entry_function,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_private:
            data["test_cases"] = self.test_cases
            data["solution_code"] = self.solution_code
        return data


class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    problem_id = Column(String, ForeignKey("problems.id"), nullable=False)
    status = Column(String, default="attempted") # "attempted", "solved"
    whiteboard_content = Column(Text, default="")
    flowchart_json = Column(Text, default="[]")
    concept_breakdown_json = Column(Text, default="{}")
    attempts_count = Column(Integer, default=1)
    last_attempt_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="progress_entries")


class Attempt(Base):
    __tablename__ = "attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    problem_id = Column(String, ForeignKey("problems.id"), nullable=False)
    code = Column(Text, default="")
    thinking_state = Column(String, default="surface_thinking")
    feedback_json = Column(Text, default="{}")
    understanding_level = Column(String, default="PROCEED")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="attempts")


class StudentKnowledge(Base):
    __tablename__ = "student_knowledge"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    mastered_topics_json = Column(Text, default="[]")
    weak_topics_json = Column(Text, default="[]")
    streak_days = Column(Integer, default=1)
    solved_count = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="knowledge")
