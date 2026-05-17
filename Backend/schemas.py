from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# ── USER ──────────────────────────────────
class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: str  # "teacher" | "student"

class UserOut(BaseModel):
    id: int
    full_name: str
    email: str
    role: str
    class Config: from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# ── TEST ──────────────────────────────────
class TestCreate(BaseModel):
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    time_limit: int  # seconds

class TestOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    category: Optional[str]
    time_limit: int
    is_active: bool
    class Config: from_attributes = True

# ── QUESTION + ANSWER ──────────────────────
class AnswerCreate(BaseModel):
    text: str
    is_correct: bool

class QuestionCreate(BaseModel):
    text: str
    order_number: int = 0
    answers: list[AnswerCreate]

class AnswerOut(BaseModel):
    id: int
    text: str
    class Config: from_attributes = True  # is_correct НЕ включаємо

class QuestionOut(BaseModel):
    id: int
    text: str
    order_number: int
    answers: list[AnswerOut]
    class Config: from_attributes = True

# ── SUBMIT ────────────────────────────────
class SubmitAnswer(BaseModel):
    question_id: int
    selected_answer_id: int

class SubmitRequest(BaseModel):
    answers: list[SubmitAnswer]

# ── RESULT ────────────────────────────────
class ResultOut(BaseModel):
    score_percent: float
    completed_at: datetime
    class Config: from_attributes = True