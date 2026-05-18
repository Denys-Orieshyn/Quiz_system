import random
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas, crud
from security import require_student

router = APIRouter(prefix="/testing", tags=["testing"])

@router.get("/start/{test_id}", response_model=list[schemas.QuestionOut])
def start_test(
    test_id: int,
    db: Session = Depends(get_db),
    student = Depends(require_student) # Доступ має тільки студент
):
    test = crud.get_test_by_id(db, test_id)
    if not test or not test.is_active:
        raise HTTPException(404, "Тест не знайдено")

    questions = test.questions
    # Змішуємо варіанти відповідей, щоб у кожного студента вони були в різному порядку
    for q in questions:
        random.shuffle(q.answers)  # перемішуємо відповіді
    # Повертаємо питання. schemas.QuestionOut автоматично приховає поле is_correct
    return questions


@router.post("/submit/{test_id}", response_model=schemas.ResultOut)
def submit_test(
    test_id: int,
    body: schemas.SubmitRequest, # JSON від студента (що він обрав)
    db: Session = Depends(get_db),
    student = Depends(require_student)
):
    test = crud.get_test_by_id(db, test_id)
    if not test:
        raise HTTPException(404, "Тест не знайдено")

    correct_ids = {
        a.id
        for q in test.questions
        for a in q.answers
        if a.is_correct
    }

    selected_ids = {ans.selected_answer_id for ans in body.answers}
    correct_count = len(correct_ids & selected_ids)
    total = len(test.questions)
    score = round(correct_count / total * 100, 1) if total > 0 else 0.0

    return crud.save_result(db, student.id, test_id, score)