"""Точка входу FastAPI-застосунку Quiz System.

У цьому файлі створюється об'єкт `app`, підключаються middleware,
реєструються роутери та виконується базова ініціалізація таблиць.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
import models  # noqa — потрібен щоб SQLAlchemy побачив моделі
from routers import users, tests, testing

# ── Створюємо всі таблиці при старті ─────────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ── FastAPI app ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="Quiz System API",
    description="Система автоматизованого тестування знань студентів",
    version="1.0.0",
    docs_url="/docs",       # Swagger UI: http://localhost:8000/docs
    redoc_url="/redoc",     # ReDoc:      http://localhost:8000/redoc
)

# ── CORS — дозволяємо запити з фронтенду ─────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # в продакшн замінити на конкретний домен
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Підключаємо роутери ───────────────────────────────────────────────────────
app.include_router(users.router)
app.include_router(tests.router)
app.include_router(testing.router)


# ── Перевірка що сервер живий ─────────────────────────────────────────────────
@app.get("/", tags=["health"])
def root():
    return {"status": "ok", "message": "Quiz System API працює ✓"}
