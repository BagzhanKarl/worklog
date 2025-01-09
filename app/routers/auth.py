import json

from flask import Blueprint, request, redirect, url_for, render_template, jsonify, make_response
from app.db import Employee
from app.utils import hash_password, check_password, generate_tokens, verify_token
from app.utils.jwttoken import token_required

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/app')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    errors = []  # Общие ошибки формы
    field_errors = {}  # Ошибки для конкретных полей

    if request.method == 'POST':
        phone = request.form.get('phone')
        password = request.form.get('password')

        # Проверка наличия данных
        if not phone:
            field_errors['phone'] = 'Введите номер телефона.'
        if not password:
            field_errors['password'] = 'Введите пароль.'

        if not field_errors:  # Если нет ошибок валидации, продолжаем проверку
            user = Employee(phone=phone).get_user_by_phone()

            if user and check_password(password, user.password):
                payload = {
                    'id': user.id,
                    'full_name': " ".join(filter(None, [user.second_name, user.first_name])),
                    'job_title': user.job_title,
                    'is_admin': user.is_admin,
                    'role_id': user.role_id,
                    'department': user.department_id,
                    'vaxta_id': user.vaxta_id,
                }
                tokens = generate_tokens(payload=payload, secret_key='worklog')

                response = make_response(redirect('/'))
                response.set_cookie('access_token', tokens['access_token'])
                response.set_cookie('refresh_token', tokens['refresh_token'])
                return response
            else:
                field_errors['phone'] = 'Пользователь с таким номером и паролем не найден.'
        else:
            errors.append('Исправьте ошибки в форме.')

    return render_template('auth/auth-signin-cover.html', errors=errors, field_errors=field_errors)



@auth_bp.route('/relogin_quick')
def relogin_quick():
    refresh_token = request.cookies.get('refresh_token')
    token_data = verify_token(refresh_token, 'worklog', 'refresh')

    # Если данные из токена в виде строки, преобразуем их в словарь
    if isinstance(token_data, str):
        token_data = json.loads(token_data)

    # Извлекаем user_id
    user_id = token_data.get('id')
    user = Employee.query.get(user_id)
    payload = {
        'id': user.id,
        'full_name': " ".join(filter(None, [user.second_name, user.first_name])),
        'job_title': user.job_title,
        'is_admin': user.is_admin,
        'role_id': user.role_id,
        'department': user.department_id,
        'vaxta_id': user.vaxta_id,
    }
    tokens = generate_tokens(payload=payload, secret_key='worklog')
    response = make_response(redirect('/'))
    response.set_cookie('access_token', tokens['access_token'])
    response.set_cookie('refresh_token', tokens['refresh_token'])
    return response



@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    response = make_response(redirect('/'))
    response.set_cookie('access_token', '0123', max_age=0)
    response.set_cookie('refresh_token', '0123', max_age=0)
    return response

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    user = Employee(
        first_name="Бағжан",
        second_name='Карл',
        third_name='Саматұлы',
        phone='+77761174378',
        password=hash_password('12345678'),
    )
    user.save_to_db()
    return jsonify({'status': 200, 'user': user.id})

@auth_bp.route('/protected')
@token_required
def protected_route():
    user = request.user  # Данные пользователя из access токена
    return f"Welcome, {user['full_name']}!"
