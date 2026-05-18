from sqlalchemy.orm import Session, selectinload
import models, schemas, security

# ── USERS ─────────────────────────────────
def get_user_by_email(db: Session, email: str):
    # SELECT * FROM users WHERE email = '...'
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, data: schemas.UserCreate):
    # Створюємо об'єкт користувача
    user = models.User(
        full_name=data.full_name, email=data.email,
        hashed_password=security.hash_password(data.password),
        role=data.role
    )
    db.add(user)  # Додаємо в сесію
    db.commit()  # Зберігаємо в базу
    db.refresh(user)  # Оновлюємо, щоб отримати з бази згенерований ID
    return user

# ── TESTS ─────────────────────────────────
def get_all_active_tests(db: Session, search: str = ""):
    q = db.query(models.Test).filter(models.Test.is_active == True)
    if search: # Якщо є рядок пошуку — шукаємо за назвою
        q = q.filter(models.Test.title.ilike(f"%{search}%"))
    return q.all()

def get_test_by_id(db: Session, test_id: int):
    return db.query(models.Test).options(
        selectinload(models.Test.questions).selectinload(models.Question.answers)
    ).filter(models.Test.id == test_id).first()

def create_test(db: Session, data: schemas.TestCreate, user_id: int):
    # **data.model_dump() розпаковує словник у параметри (title=..., description=...)
    test = models.Test(**data.model_dump(), created_by=user_id)
    db.add(test); db.commit(); db.refresh(test)
    return test

def update_test(db: Session, test_id: int, data: schemas.TestCreate):
    test = get_test_by_id(db, test_id)
    for k, v in data.model_dump().items():
        setattr(test, k, v) # Оновлюємо атрибути об'єкта
    db.commit(); db.refresh(test)
    return test

def delete_test(db: Session, test_id: int):
    test = get_test_by_id(db, test_id)
    db.delete(test); db.commit() # Завдяки Cascade, видаляться і всі питання

# ── QUESTIONS ─────────────────────────────
def create_question_with_answers(
    db: Session, test_id: int, data: schemas.QuestionCreate
):
    # Транзакція: створюємо питання
    question = models.Question(
        test_id=test_id, text=data.text,
        order_number=data.order_number
    )
    db.add(question); db.flush() # flush() дає питанню ID, але ще не зберігає остаточно
    # У циклі створюємо відповіді, прив'язуючи їх до ID питання
    for a in data.answers:
        db.add(models.Answer(
            question_id=question.id,
            text=a.text, is_correct=a.is_correct
        ))
    db.commit(); db.refresh(question) # Зберігаємо і питання, і відповіді одночасно
    return question

# ── RESULTS ───────────────────────────────
def save_result(db: Session, user_id: int,
                test_id: int, score: float):
    result = models.TestResult(
        user_id=user_id, test_id=test_id,
        score_percent=score
    )
    db.add(result); db.commit(); db.refresh(result)
    return result

def get_results_by_test(db: Session, test_id: int):
    # Повертає результати, відсортовані від найвищого балу до найнижчого
    return db.query(models.TestResult).options(
        selectinload(models.TestResult.student)
    ).filter(
        models.TestResult.test_id == test_id
    ).order_by(models.TestResult.score_percent.desc()).all()
