"""Pydantic-схеми для валідації вхідних і вихідних даних API.

Схеми відокремлюють внутрішні моделі БД від JSON, який отримує або
надсилає клієнт. Саме тут приховується `is_correct` від студентів.
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


# ── USER ──────────────────────────────────
# Те, що ми вимагаємо від юзера при реєстрації
class UserCreate(BaseModel):
    full_name: str
    email: EmailStr  # Автоматично перевіряє, чи є символ @
    password: str
    role: str


# Те, що ми повертаємо клієнту (пароля тут немає — це безпека)
class UserOut(BaseModel):
    id: int
    full_name: str
    email: str
    role: str

    # from_attributes дозволяє Pydantic конвертувати об'єкти БД (SQLAlchemy) в JSON
    class Config: from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


# ── TEST ──────────────────────────────────
class TestCreate(BaseModel):
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    time_limit: int  # Час у секундах


class TestOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    category: Optional[str]
    time_limit: int
    is_active: bool

    class Config: from_attributes = True


# ── QUESTION + ANSWER ──────────────────────
# Дані для СТВОРЕННЯ відповіді (викладач відправляє це на сервер)
class AnswerCreate(BaseModel):
    text: str
    is_correct: bool


class QuestionCreate(BaseModel):
    text: str
    order_number: int = 0
    answers: list[AnswerCreate]


# Дані для ВІДОБРАЖЕННЯ відповіді студенту.
# ВАЖЛИВО: тут немає поля is_correct! Тому студент ніяк не дізнається правильну відповідь.
class AnswerOut(BaseModel):
    id: int
    text: str

    class Config: from_attributes = True


class QuestionOut(BaseModel):
    id: int
    text: str
    order_number: int
    answers: list[AnswerOut]

    class Config: from_attributes = True


# ── SUBMIT (Відправка відповідей) ──────────
# Формат: яке питання і які варіанти обрав студент
class SubmitAnswer(BaseModel):
    question_id: int
    selected_answer_id: Optional[int] = None
    selected_answer_ids: list[int] = Field(default_factory=list)

    def selected_ids(self) -> set[int]:
        if self.selected_answer_ids:
            return set(self.selected_answer_ids)
        if self.selected_answer_id is not None:
            return {self.selected_answer_id}
        return set()


class SubmitRequest(BaseModel):
    answers: list[SubmitAnswer]


# ── RESULT ────────────────────────────────
class ResultOut(BaseModel):
    score_percent: float
    completed_at: datetime

    class Config: from_attributes = True
