"""Налаштування підключення до PostgreSQL через SQLAlchemy.

Файл відповідає за читання змінних середовища, створення engine,
фабрики сесій та залежності `get_db()` для FastAPI endpoints.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings

# Клас Settings автоматично зчитує змінні з файлу .env
class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env"

# Створюємо об'єкт налаштувань
settings = Settings()

# Двигун (engine) — це головний "мотор" SQLAlchemy, який підключається до БД
engine = create_engine(settings.DATABASE_URL)

# Фабрика сесій. Кожен раз, коли нам треба звернутися до БД, ми створюємо нову сесію
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовий клас, від якого ми будемо наслідувати всі наші моделі (таблиці)
Base = declarative_base()

# Спеціальна функція (генератор), яка видає сесію бази даних для запитів FastAPI.
# Після виконання запиту вона автоматично закриває з'єднання (db.close()), щоб не перевантажувати пам'ять.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
