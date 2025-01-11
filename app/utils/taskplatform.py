import random
import string

def generate_unique_id(length=6):
    """
    Генерирует уникальный ID из заданного количества символов,
    состоящего из цифр и больших латинских букв.

    :param length: Длина ID (по умолчанию 6)
    :return: Строка с уникальным ID
    """
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choices(characters, k=length))

