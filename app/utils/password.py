import bcrypt


def hash_password(password: str) -> str:
    """
    Хеширует пароль для безопасного хранения.

    :param password: Пароль в виде строки
    :return: Хешированный пароль в виде строки
    """
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')


def check_password(password: str, hashed_password: str) -> bool:
    """
    Проверяет пароль на соответствие хешу.

    :param password: Пароль в виде строки
    :param hashed_password: Хешированный пароль
    :return: True, если пароль совпадает, иначе False
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

