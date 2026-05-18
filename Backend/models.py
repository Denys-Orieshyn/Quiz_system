from sqlalchemy import Column, Integer, String, Boolean, Float
from sqlalchemy import ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    # Створюємо колонки (поля) таблиці
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False)  # nullable=False означає, що поле не може бути пустим
    email = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)  # Ролі: "teacher" або "student"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())  # Автоматично ставить поточний час

    # relationship — це "віртуальні" зв'язки для зручності в Python.
    # cascade="all, delete" означає: якщо видалити юзера, всі його тести і результати теж видаляться
    tests = relationship("Test", back_populates="author", cascade="all, delete")
    results = relationship("TestResult", back_populates="student", cascade="all, delete")

class Test(Base):
    __tablename__ = "tests"
    id          = Column(Integer, primary_key=True, index=True)
    title       = Column(String(200), nullable=False, index=True)
    description = Column(String, nullable=True)
    category    = Column(String(100), nullable=True)
    time_limit  = Column(Integer, nullable=False)   # Час у секундах
    is_active   = Column(Boolean, default=True)
    # Зовнішній ключ, який вказує на автора (users.id)
    created_by  = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    created_at  = Column(DateTime, server_default=func.now())

    author      = relationship("User", back_populates="tests")
    questions   = relationship("Question", back_populates="test", cascade="all, delete", order_by="Question.order_number")
    results     = relationship("TestResult", back_populates="test", cascade="all, delete")


class Question(Base):
    __tablename__ = "questions"
    id           = Column(Integer, primary_key=True, index=True)
    test_id      = Column(Integer, ForeignKey("tests.id", ondelete="CASCADE"))
    text         = Column(String, nullable=False)
    order_number = Column(Integer, default=0) # Порядок відображення питань
    created_at   = Column(DateTime, server_default=func.now())

    test         = relationship("Test", back_populates="questions")
    answers      = relationship("Answer", back_populates="question", cascade="all, delete")


class Answer(Base):
    __tablename__ = "answers"
    id          = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"))
    text        = Column(String, nullable=False)
    is_correct  = Column(Boolean, default=False) # Головний маркер: чи правильна ця відповідь
    created_at  = Column(DateTime, server_default=func.now())

    question    = relationship("Question", back_populates="answers")

class TestResult(Base):
    __tablename__ = "test_results"
    id            = Column(Integer, primary_key=True, index=True)
    user_id       = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    test_id       = Column(Integer, ForeignKey("tests.id", ondelete="CASCADE"))
    score_percent = Column(Float, nullable=False) # Зберігаємо відсоток: 85.5
    completed_at  = Column(DateTime, server_default=func.now())
    created_at    = Column(DateTime, server_default=func.now())

    student       = relationship("User", back_populates="results")
    test          = relationship("Test", back_populates="results")
