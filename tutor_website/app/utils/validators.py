# app/utils/validators.py
import re
from typing import Tuple, Optional


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """Проверить валидность email"""
    if not email:
        return False, "Email не может быть пустым"

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Неверный формат email"

    return True, None


def validate_password(password: str) -> Tuple[bool, Optional[str]]:
    """Проверить валидность пароля"""
    if not password:
        return False, "Пароль не может быть пустым"

    if len(password) < 8:
        return False, "Пароль должен быть не менее 8 символов"

    if not any(char.isdigit() for char in password):
        return False, "Пароль должен содержать хотя бы одну цифру"

    if not any(char.isalpha() for char in password):
        return False, "Пароль должен содержать хотя бы одну букву"

    return True, None