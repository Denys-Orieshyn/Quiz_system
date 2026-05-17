from sqlalchemy import Column, Integer, String, Boolean, Float
from sqlalchemy import ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    id            = Column(Integer, primary_key=True, index=True)
    full_name     = Column(String(150), nullable=False)
    email         = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role          = Column(String(20), nullable=False)  # "teacher" | "student"
    is_active     = Column(Boolean, default=True)
    created_at    = Column(DateTime, server_default=func.now())

    tests         = relationship("Test", back_populates="author",
                                 cascade="all, delete")
    results       = relationship("TestResult", back_populates="student",
                                 cascade="all, delete")


class Test(Base):
    __tablename__ = "tests"
    id          = Column(Integer, primary_key=True, index=True)
    title       = Column(String(200), nullable=False, index=True)
    description = Column(String, nullable=True)
    category    = Column(String(100), nullable=True)
    time_limit  = Column(Integer, nullable=False)   # seconds
    is_active   = Column(Boolean, default=True)
    created_by  = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    created_at  = Column(DateTime, server_default=func.now())

    author      = relationship("User", back_populates="tests")
    questions   = relationship("Question", back_populates="test",
                               cascade="all, delete")
    results     = relationship("TestResult", back_populates="test",
                               cascade="all, delete")


class Question(Base):
    __tablename__ = "questions"
    id           = Column(Integer, primary_key=True, index=True)
    test_id      = Column(Integer, ForeignKey("tests.id", ondelete="CASCADE"))
    text         = Column(String, nullable=False)
    order_number = Column(Integer, default=0)
    created_at   = Column(DateTime, server_default=func.now())

    test         = relationship("Test", back_populates="questions")
    answers      = relationship("Answer", back_populates="question",
                                cascade="all, delete")


class Answer(Base):
    __tablename__ = "answers"
    id          = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"))
    text        = Column(String, nullable=False)
    is_correct  = Column(Boolean, default=False)
    created_at  = Column(DateTime, server_default=func.now())

    question    = relationship("Question", back_populates="answers")


class TestResult(Base):
    __tablename__ = "test_results"
    id            = Column(Integer, primary_key=True, index=True)
    user_id       = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    test_id       = Column(Integer, ForeignKey("tests.id", ondelete="CASCADE"))
    score_percent = Column(Float, nullable=False)
    completed_at  = Column(DateTime, server_default=func.now())
    created_at    = Column(DateTime, server_default=func.now())

    student       = relationship("User", back_populates="results")
    test          = relationship("Test", back_populates="results")