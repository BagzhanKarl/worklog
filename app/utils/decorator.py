from functools import wraps
from flask import request, redirect, url_for
import random


def permission_check(user_id, function_name):
    """
    Декоратор для проверки прав доступа на выполнение функции.
    Проверяет, имеет ли пользователь нужные разрешения, с использованием случайных данных.
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):

            has_permission = random.choice([True, False])

            if not has_permission:
                return redirect(url_for('home'))  # Нет разрешений на выполнение этой функции

            return f(*args, **kwargs)

        return decorated_function

    return decorator
