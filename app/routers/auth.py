import json
from flask import Blueprint, request, redirect, url_for, render_template, jsonify, make_response
from app.db import User, db, UserPermission, Permission, RolePermission
from app.utils import hash_password, check_password, generate_tokens, verify_token
from app.utils.jwttoken import token_required

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/app')


def get_user_permission(user_id):
    try:
        # Делаем JOIN для оптимизации запросов
        permissions = db.session.query(
            Permission.function,
            Permission.name,
            UserPermission.is_granted
        ).join(
            UserPermission,
            Permission.id == UserPermission.permission_id
        ).filter(
            UserPermission.user_id == user_id
        ).all()

        return [
            {
                'function': perm.function,
                'name': perm.name,
                'is_granted': str(perm.is_granted).lower()  # Преобразуем в строку 'true' или 'false'
            }
            for perm in permissions
        ]
    except Exception as e:
        print(f"Error getting permissions: {str(e)}")
        return []


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    errors = []
    field_errors = {}

    if request.method == 'POST':
        try:
            phone = request.form.get('phone', '').strip()
            password = request.form.get('password', '').strip()

            # Валидация
            if not phone:
                field_errors['phone'] = 'Введите номер телефона.'
            if not password:
                field_errors['password'] = 'Введите пароль.'

            if not field_errors:
                user = User.query.filter_by(phone=phone).first()

                if user and user.check_password(password):
                    UserPermission.query.filter_by(user_id=user.id).delete()
                    if user.role_id != 1:
                        ps = RolePermission.query.filter_by(role_id=user.role_id).all()
                        for permission in ps:
                            user_perm = UserPermission(
                                user_id=user.id,
                                permission_id=permission.permission_id,
                                is_granted=permission.is_granted
                            )
                            db.session.add(user_perm)
                        db.session.commit()
                    else:
                        permissions = Permission.query.all()
                        if permissions:
                            for permission in permissions:
                                user_perm = UserPermission(
                                    user_id=user.id,
                                    permission_id=permission.id,
                                    is_granted=True
                                )
                                db.session.add(user_perm)
                            db.session.commit()

                    # Формируем payload
                    payload = {
                        'id': user.id,
                        'full_name': f"{user.second_name} {user.first_name}".strip(),
                        'job_title': user.job_title,
                        'is_admin': user.is_admin,
                        'role_id': user.role_id,
                        'department_id': user.department_id,
                        'shift_id': user.shift_id,
                    }

                    # Генерируем токены
                    tokens = generate_tokens(payload=payload, secret_key='worklog')

                    # Получаем права пользователя
                    rules = get_user_permission(user.id)

                    # Создаем response
                    response = make_response(redirect('/'))

                    # Устанавливаем токены
                    response.set_cookie('access_token', tokens['access_token'],
                                        httponly=True, secure=True)  # Добавляем безопасность
                    response.set_cookie('refresh_token', tokens['refresh_token'],
                                        httponly=True, secure=True)

                    # Устанавливаем права
                    for rule in rules:
                        # Используем безопасное имя для cookie
                        cookie_name = f"perm_{rule['function']}"
                        response.set_cookie(
                            cookie_name,
                            rule['is_granted'],
                            httponly=True,
                            secure=True
                        )

                    return response
                else:
                    field_errors['password'] = 'Неверный номер телефона или пароль.'
        except Exception as e:
            errors.append(f'Произошла ошибка при входе. Попробуйте позже.')
            print(f"Login error: {str(e)}")

    return render_template('auth/auth-signin-cover.html',
                           errors=errors,
                           field_errors=field_errors)
@auth_bp.route('/relogin_quick')
def relogin_quick():
    refresh_token = request.cookies.get('refresh_token')
    token_data = verify_token(refresh_token, 'worklog', 'refresh')

    # Если данные из токена в виде строки, преобразуем их в словарь
    if isinstance(token_data, str):
        token_data = json.loads(token_data)

    # Извлекаем user_id
    user_id = token_data.get('id')
    user = User.query.get(user_id)
    if not user:
        return redirect('/app/login')

    # Подготавливаем данные пользователя для токенов
    payload = {
        'id': user.id,
        'full_name': f"{user.second_name} {user.first_name}",
        'job_title': user.job_title,
        'is_admin': user.is_admin,
        'role_id': user.role_id,
        'department_id': user.department_id,
        'shift_id': user.shift_id,
    }
    tokens = generate_tokens(payload=payload, secret_key='worklog')

    # Получаем параметр next из запроса
    next_url = request.args.get('next', '/')  # По умолчанию на главную страницу

    # Устанавливаем новые токены и перенаправляем на страницу, указанную в next
    response = make_response(redirect(next_url))
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
    user = User(
        first_name='Бағжан',
        second_name='Карл',
        third_name='Саматұлы',
        phone='+77761174378',
        password=hash_password('12345678'),
    )
    db.session.add(user)
    db.session.commit()


@auth_bp.route('/protected')
@token_required
def protected_route():
    user = request.user  # Данные пользователя из access токена
    return f"Welcome, {user['full_name']}!"
