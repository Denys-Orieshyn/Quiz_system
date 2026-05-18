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
    if not test:
        raise HTTPException(404, "Тест не знайдено")

    # Будуємо словник: { question_id -> selected_answer_id }
    # для швидкого пошуку відповіді студента по кожному питанню
    student_answers = {
        ans.question_id: ans.selected_answer_id
        for ans in body.answers
    }

    questions = test.questions
    total = len(questions)

    if total == 0:
        score = 0.0
    else:
        correct_questions = 0

        for question in questions:
            selected_id = student_answers.get(question.id)

            # Якщо студент не відповів на питання — питання зараховується як неправильне
            if selected_id is None:
                continue

            # Знаходимо обрану відповідь серед варіантів цього питання
            selected_answer = next(
                (a for a in question.answers if a.id == selected_id),
                None
            )

            # Питання вважається правильно відповіденим,
            # якщо обрана відповідь є правильною (is_correct == True)
            if selected_answer and selected_answer.is_correct:
                correct_questions += 1

        # Бал = кількість правильно відповіджених питань / загальна кількість питань
        # Формула працює ЗАВЖДИ коректно, незалежно від кількості правильних варіантів
        score = round(correct_questions / total * 100, 1)

    return crud.save_result(db, student.id, test_id, score)