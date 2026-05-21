import os
os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost:5432/db"
os.environ["SECRET_KEY"] = "super_secret_test_key"

from security import hash_password, verify_password

def test_hash_password():
    # Перевірка, що хеш не дорівнює відкритому паролю
    pwd = "super_secret_password"
    assert hash_password(pwd) != pwd

def test_verify_password_correct():
    # Правильний пароль -> True
    pwd = "super_secret_password"
    hashed = hash_password(pwd)
    assert verify_password(pwd, hashed) is True

def test_verify_password_wrong():
    # Неправильний пароль -> False
    pwd = "super_secret_password"
    hashed = hash_password(pwd)
    assert verify_password("wrong_password", hashed) is False