from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import get_db, settings
import models

# Налаштовуємо алгоритм хешування bcrypt (він дуже надійний)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Вказуємо FastAPI, де знаходиться URL для отримання токена
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

def hash_password(password: str) -> str:
    # Перетворює звичайний пароль "123456" на нечитабельний хеш
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    # Порівнює введений пароль з хешем із БД
    return pwd_context.verify(plain, hashed)

def create_jwt_token(data: dict) -> str:
    # Задаємо час, коли токен "згорить" (через 60 хвилин)
    expire = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    # Шифруємо дані (ID юзера і роль) за допомогою секретного ключа
    return jwt.encode(
        {**data, "exp": expire},
        settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
# Ця функція викликається при кожному запиті, де потрібна авторизація
def get_current_user(
    token: str = Depends(oauth2_scheme), # FastAPI сам дістане токен із заголовків
    db: Session = Depends(get_db)
) -> models.User:
    exc = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Невалідний токен")
    try:
        # Розшифровуємо токен
        payload = jwt.decode(token, settings.SECRET_KEY,
                             algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise exc
    except JWTError:
        raise exc
    # Шукаємо юзера в базі
    user = db.query(models.User).filter(
        models.User.id == user_id).first()
    if not user:
        raise exc
    return user

# Перевірка прав (Role-Based Access Control)
def require_teacher(user: models.User = Depends(get_current_user)):
    if user.role != "teacher":
        raise HTTPException(status_code=403, detail="Тільки для викладача")
    return user

def require_student(user: models.User = Depends(get_current_user)):
    if user.role != "student":
        raise HTTPException(status_code=403, detail="Тільки для студента")
    return user