from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
import schemas, crud, security

router = APIRouter(prefix="/users", tags=["users"])


# ── Реєстрація ────────────────────────────────────────────────────────────────
@router.post("/register", response_model=schemas.UserOut)
def register(data: schemas.UserCreate, db: Session = Depends(get_db)):
    if data.role not in ("teacher", "student"):
        raise HTTPException(400, "Роль повинна бути 'teacher' або 'student'")
    if crud.get_user_by_email(db, data.email):
        raise HTTPException(400, "Користувач з таким email вже існує")
    return crud.create_user(db, data)


# ── Логін (повертає JWT токен) ────────────────────────────────────────────────
@router.post("/login", response_model=schemas.Token)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = crud.get_user_by_email(db, form.username)
    if not user or not security.verify_password(form.password, user.hashed_password):
        raise HTTPException(401, "Невірний email або пароль")
    if not user.is_active:
        raise HTTPException(403, "Обліковий запис деактивовано")
    token = security.create_jwt_token({
        "sub": str(user.id),
        "role": user.role
    })
    return {"access_token": token, "token_type": "bearer"}


# ── Отримати поточного користувача ────────────────────────────────────────────
@router.get("/me", response_model=schemas.UserOut)
def get_me(user=Depends(security.get_current_user)):
    return user