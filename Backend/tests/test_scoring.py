import os

os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost:5432/db"
os.environ["SECRET_KEY"] = "super_secret_test_key"


# Функція, що відтворює логіку підрахунку з testing.py
def calculate_score(correct_count: int, total_count: int) -> float:
    if total_count == 0:
        return 0.0
    return round((correct_count / total_count) * 100, 1)

def test_score_all_correct():
    assert calculate_score(3, 3) == 100.0

def test_score_partial():
    assert calculate_score(1, 3) == 33.3

def test_score_none_answered():
    assert calculate_score(0, 3) == 0.0

def test_score_empty_test():
    assert calculate_score(0, 0) == 0.0