import jwt
from datetime import datetime, timedelta
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from functools import wraps
from flask import request, jsonify, redirect, url_for
from datetime import datetime

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Извлекаем токены из cookies
        access_token = request.cookies.get('access_token')
        refresh_token = request.cookies.get('refresh_token')

        # Проверяем access токен
        if access_token:
            try:
                decoded_token = jwt.decode(access_token, 'worklog', algorithms=["HS256"])

                # Проверяем тип токена
                if decoded_token.get('type') != 'access':
                    raise jwt.InvalidTokenError

                # Передаем данные пользователя
                request.user = decoded_token
                return f(*args, **kwargs)
            except jwt.ExpiredSignatureError:
                pass  # Истекший access токен будет обработан ниже
            except jwt.InvalidTokenError:
                pass  # Неверный access токен будет обработан ниже

        # Если access токен невалидный, проверяем refresh токен
        if refresh_token:
            try:
                decoded_refresh = jwt.decode(refresh_token, 'worklog', algorithms=["HS256"])

                # Проверяем тип токена
                if decoded_refresh.get('type') != 'refresh':
                    raise jwt.InvalidTokenError

                # Перенаправляем на быстрый релогин
                return redirect(url_for('auth_bp.relogin_quick'))
            except jwt.ExpiredSignatureError:
                return redirect(url_for('auth_bp.login'))  # Refresh токен истек
            except jwt.InvalidTokenError:
                return redirect(url_for('auth_bp.login'))  # Refresh токен недействителен

        # Если оба токена неверны или отсутствуют, перенаправляем на страницу входа
        return redirect(url_for('auth_bp.login'))

    return decorated_function



def generate_tokens(payload: dict, secret_key: str, access_expiry: int = 3600, refresh_expiry: int = 604800) -> dict:
    """
    Генерирует Access и Refresh токены.

    :param payload: Данные для токенов в виде словаря
    :param secret_key: Секретный ключ для подписи токенов
    :param access_expiry: Срок действия Access Token в секундах (по умолчанию 1 час)
    :param refresh_expiry: Срок действия Refresh Token в секундах (по умолчанию 7 дней)
    :return: Словарь с Access и Refresh токенами
    """
    current_time = datetime.utcnow()

    # Создаем payload для Access Token
    access_payload = payload.copy()
    access_payload.update({
        'exp': current_time + timedelta(seconds=access_expiry),
        'iat': current_time,
        'type': 'access'
    })
    access_token = jwt.encode(access_payload, secret_key, algorithm="HS256")

    # Создаем payload для Refresh Token
    refresh_payload = {'id': payload['id']}
    refresh_payload.update({
        'exp': current_time + timedelta(seconds=refresh_expiry),
        'iat': current_time,
        'type': 'refresh'
    })
    refresh_token = jwt.encode(refresh_payload, secret_key, algorithm="HS256")

    return {
        'access_token': access_token,
        'refresh_token': refresh_token
    }


def verify_token(token: str, secret_key: str, expected_type: str) -> dict:
    """
    Проверяет JWT токен на валидность и соответствие типу.

    :param token: JWT токен
    :param secret_key: Секретный ключ, используемый для подписи токенов
    :param expected_type: Ожидаемый тип токена ('access' или 'refresh')
    :return: Расшифрованный payload токена, если он валиден
    :raises: ValueError, если токен недействителен
    """
    try:
        # Декодируем токен
        decoded_token = jwt.decode(token, secret_key, algorithms=["HS256"])

        # Проверяем тип токена
        if decoded_token.get('type') != expected_type:
            raise ValueError(f"Invalid token type. Expected: {expected_type}, got: {decoded_token.get('type')}")

        return decoded_token
    except ExpiredSignatureError:
        raise ValueError("Token has expired")
    except InvalidTokenError as e:
        raise ValueError(f"Invalid token: {str(e)}")
