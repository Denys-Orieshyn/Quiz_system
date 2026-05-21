"""API-роутер проходження тестів студентом.

Відповідає за старт тесту, перемішування відповідей без передачі
`is_correct` клієнту та підрахунок фінального відсоткового результату.
"""

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
    student=Depends(require_student)
):
    test = crud.get_test_by_id(db, test_id)
    if not test or not test.is_active:
        raise HTTPException(404, "Тест не знайдено")

    questions = test.questions
    # Перемішуємо варіанти відповідей для кожного питання
    # is_correct НЕ потрапить до клієнта — це визначено схемою AnswerOut
    for q in questions:
        random.shuffle(q.answers)

    return questions


@router.post("/submit/{test_id}", response_model=schemas.ResultOut)
def submit_test(
    test_id: int,
    body: schemas.SubmitRequest,
    db: Session = Depends(get_db),
    student=Depends(require_student)
):
    test = crud.get_test_by_id(db, test_id)
    if not test or not test.is_active:
        raise HTTPException(404, "Тест не знайдено")

    # Будуємо словник: { question_id -> selected_answer_ids }
    # для швидкого пошуку відповідей студента по кожному питанню
    student_answers: dict[int, set[int]] = {}
    for ans in body.answers:
        student_answers.setdefault(ans.question_id, set()).update(ans.selected_ids())

    questions = test.questions
    total = len(questions)

    if total == 0:
        score = 0.0
    else:
        correct_questions = 0

        for question in questions:
            selected_ids = student_answers.get(question.id, set())

            # Якщо студент не відповів на питання — питання зараховується як неправильне
            if not selected_ids:
                continue

            # Знаходимо всі правильні відповіді серед варіантів цього питання
            correct_answer_ids = {
                a.id for a in question.answers
                if a.is_correct
            }

            # Питання вважається правильно відповіденим,
            # якщо обрано рівно всі правильні відповіді без зайвих варіантів
            if selected_ids == correct_answer_ids:
                correct_questions += 1

        # Бал = кількість правильно відповіджених питань / загальна кількість питань
        # Формула працює ЗАВЖДИ коректно, незалежно від кількості правильних варіантів
        score = round(correct_questions / total * 100, 1)

    return crud.save_result(db, student.id, test_id, score)

@router.get("/my-results")
def get_my_results(
    db: Session = Depends(get_db),
    student=Depends(require_student)
):
    """Повертає всі результати тестувань поточного студента."""
    results = crud.get_results_by_user(db, student.id)
    return [
        {
            "test_title":    r.test.title,
            "score_percent": r.score_percent,
            "completed_at":  r.completed_at.isoformat()
        }
        for r in results
    ]
