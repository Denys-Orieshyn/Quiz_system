from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
import models, schemas, crud
from security import require_teacher, get_current_user

router = APIRouter(prefix="/tests", tags=["tests"])


# ── Отримати всі активні тести (студент і викладач) ──────────────────────────
@router.get("/", response_model=List[schemas.TestOut])
def get_tests(
    search: Optional[str] = "",
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return crud.get_all_active_tests(db, search)


# ── Отримати всі тести викладача (включно з неактивними) ─────────────────────
@router.get("/my", response_model=List[schemas.TestOut])
def get_my_tests(
    db: Session = Depends(get_db),
    teacher=Depends(require_teacher)
):
    return db.query(models.Test).filter(
        models.Test.created_by == teacher.id
    ).all()


# ── Отримати конкретний тест ──────────────────────────────────────────────────
@router.get("/{test_id}", response_model=schemas.TestOut)
def get_test(
    test_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    test = crud.get_test_by_id(db, test_id)
    if not test:
        raise HTTPException(404, "Тест не знайдено")
    return test


# ── Створити тест ─────────────────────────────────────────────────────────────
@router.post("/", response_model=schemas.TestOut)
def create_test(
    data: schemas.TestCreate,
    db: Session = Depends(get_db),
    teacher=Depends(require_teacher)
):
    return crud.create_test(db, data, teacher.id)


# ── Оновити тест ──────────────────────────────────────────────────────────────
@router.put("/{test_id}", response_model=schemas.TestOut)
def update_test(
    test_id: int,
    data: schemas.TestCreate,
    db: Session = Depends(get_db),
    teacher=Depends(require_teacher)
):
    test = crud.get_test_by_id(db, test_id)
    if not test or test.created_by != teacher.id:
        raise HTTPException(404, "Тест не знайдено або немає доступу")
    return crud.update_test(db, test_id, data)


# ── Видалити тест ─────────────────────────────────────────────────────────────
@router.delete("/{test_id}")
def delete_test(
    test_id: int,
    db: Session = Depends(get_db),
    teacher=Depends(require_teacher)
):
    test = crud.get_test_by_id(db, test_id)
    if not test or test.created_by != teacher.id:
        raise HTTPException(404, "Тест не знайдено або немає доступу")
    crud.delete_test(db, test_id)
    return {"detail": "Тест видалено"}


# ── Активувати / деактивувати тест ───────────────────────────────────────────
@router.patch("/{test_id}/toggle")
def toggle_test(
    test_id: int,
    db: Session = Depends(get_db),
    teacher=Depends(require_teacher)
):
    test = crud.get_test_by_id(db, test_id)
    if not test or test.created_by != teacher.id:
        raise HTTPException(404, "Тест не знайдено")
    test.is_active = not test.is_active
    db.commit()
    return {"is_active": test.is_active}


# ── Додати питання до тесту ───────────────────────────────────────────────────
@router.post("/{test_id}/questions")
def add_question(
    test_id: int,
    data: schemas.QuestionCreate,
    db: Session = Depends(get_db),
    teacher=Depends(require_teacher)
):
    test = crud.get_test_by_id(db, test_id)
    if not test or test.created_by != teacher.id:
        raise HTTPException(404, "Тест не знайдено")
    if not any(a.is_correct for a in data.answers):
        raise HTTPException(400, "Питання повинно мати хоча б одну правильну відповідь")
    return crud.create_question_with_answers(db, test_id, data)


# ── Отримати питання тесту (для викладача — з is_correct) ────────────────────
@router.get("/{test_id}/questions")
def get_questions(
    test_id: int,
    db: Session = Depends(get_db),
    teacher=Depends(require_teacher)
):
    test = crud.get_test_by_id(db, test_id)
    if not test or test.created_by != teacher.id:
        raise HTTPException(404, "Тест не знайдено")
    result = []
    for q in test.questions:
        result.append({
            "id": q.id,
            "text": q.text,
            "order_number": q.order_number,
            "answers": [
                {"id": a.id, "text": a.text, "is_correct": a.is_correct}
                for a in q.answers
            ]
        })
    return result


# ── Видалити питання ──────────────────────────────────────────────────────────
@router.delete("/questions/{question_id}")
def delete_question(
    question_id: int,
    db: Session = Depends(get_db),
    teacher=Depends(require_teacher)
):
    q = db.query(models.Question).join(models.Test).filter(
        models.Question.id == question_id,
        models.Test.created_by == teacher.id
    ).first()
    if not q:
        raise HTTPException(404, "Питання не знайдено")
    db.delete(q)
    db.commit()
    return {"detail": "Питання видалено"}


# ── Статистика тесту ──────────────────────────────────────────────────────────
@router.get("/{test_id}/statistics")
def get_statistics(
    test_id: int,
    db: Session = Depends(get_db),
    teacher=Depends(require_teacher)
):
    test = crud.get_test_by_id(db, test_id)
    if not test or test.created_by != teacher.id:
        raise HTTPException(404, "Тест не знайдено")
    results = crud.get_results_by_test(db, test_id)
    return [
        {
            "student_name": r.student.full_name,
            "score_percent": r.score_percent,
            "completed_at": r.completed_at.isoformat()
        }
        for r in results
    ]
