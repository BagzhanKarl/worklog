from flask import Blueprint, request, render_template, redirect, url_for
from app.db import db, User, Department, Shift, Role, Permission
from app.utils import token_required

users = Blueprint('users', __name__, url_prefix='/users')


# Просмотр всех пользователей
@users.route('/', methods=['GET'])
@token_required
def get_all_users():
    user_rest = request.user
    permission_on_db = Permission.query.filter_by(page='users').all()
    permission = []
    for item in permission_on_db:
        perm_current = request.cookies.get(f'perm_{item.function}')
        permission.append({item.function: perm_current})
    print(permission)

    users = User.query.order_by(User.role_id.asc()).all()  # Получаем всех пользователей
    response = []
    for user in users:
        if user.role_id == 1:
            continue
        initials = user.first_name[0].upper() + user.second_name[0].upper()
        dep = Department.query.filter_by(id=user.department_id).first()
        shift = Shift.query.filter_by(id=user.shift_id).first()
        response.append(
            {
                "id": user.id,
                "initials": initials,
                "first_name": user.first_name,
                "second_name": user.second_name,
                "third_name": user.third_name,
                "phone": user.phone,
                "department": dep.name if dep else "Нету",
                "position": user.job_title,
                "shift": shift.title if shift else "Нету",
                "status": True if shift and shift.is_active else False,
            }
        )
    departments = Department.get_all()
    return render_template('users/all-users.html', user=user_rest, roles=Role.get_all(), shifts=Shift.get_all(), departments=departments, users=response, permission=permission)


# Просмотр данных конкретного пользователя
@users.route('/<int:user_id>', methods=['GET'])
@token_required
def get_user_details(user_id):
    user = User.get_by_id(user_id)  # Получаем пользователя по ID
    return render_template('users/user_details.html', user=user)


# Создание нового пользователя
@users.route('/create', methods=['GET', 'POST'])
@token_required
def create_user():
    if request.method == 'POST':
        first_name = request.form['first_name']
        second_name = request.form['second_name']
        third_name = request.form.get('third_name', '')
        phone = request.form.get('phone', '')
        job_title = request.form.get('position', '')
        password = request.form['password']
        is_admin = request.form.get('is_admin', False)
        department_id = request.form.get('department_id')
        shift_id = request.form.get('shift_id')
        role_id = request.form.get('role_id')

        department_id = int(department_id) if department_id != "0" is not None else None
        shift_id = int(shift_id) if shift_id != "0" is not None else None
        role_id = int(role_id) if role_id != "0" is not None else None

        new_user = User(first_name=first_name, second_name=second_name, third_name=third_name,
                        phone=phone, job_title=job_title, is_admin=is_admin, department_id=department_id,
                        shift_id=shift_id, role_id=role_id)
        new_user.set_password(password)  # Хешируем пароль
        new_user.save_to_db()  # Сохраняем пользователя в базе данных
        return redirect(url_for('users.get_all_users'))  # Перенаправляем на страницу всех пользователей

    return render_template('users/create_user.html')


# Обновление пользователя
@users.route('/update/<int:user_id>', methods=['GET', 'POST'])
@token_required
def update_user(user_id):
    user = User.get_by_id(user_id)

    if request.method == 'POST':
        user.first_name = request.form['first_name']
        user.second_name = request.form['second_name']
        user.third_name = request.form.get('third_name', '')
        user.phone = request.form.get('phone', '')
        user.job_title = request.form.get('job_title', '')
        user.department_id = request.form.get('department_id')
        user.shift_id = request.form.get('shift_id')

        if request.form.get('password'):
            user.set_password(request.form['password'])  # Обновляем пароль

        user.save_to_db()  # Сохраняем изменения в базе данных
        return redirect(url_for('users.get_all_users'))  # Перенаправляем на страницу всех пользователей

    return render_template('users/update_user.html', user=user)


# Удаление пользователя
@users.route('/delete/<int:user_id>', methods=['POST'])
@token_required
def delete_user(user_id):
    user = User.get_by_id(user_id)
    user.delete_account()  # Удаляем пользователя (помечаем как удаленный)
    return redirect(url_for('users.get_all_users'))  # Перенаправляем на страницу всех пользователей


# Активация пользователя
@users.route('/activate/<int:user_id>', methods=['POST'])
@token_required
def activate_user(user_id):
    user = User.get_by_id(user_id)
    user.activate_account()  # Активируем пользователя
    return redirect(url_for('users.get_all_users'))  # Перенаправляем на страницу всех пользователей


# Деактивация пользователя
@users.route('/deactivate/<int:user_id>', methods=['POST'])
@token_required
def deactivate_user(user_id):
    user = User.get_by_id(user_id)
    user.deactivate_account()  # Деактивируем пользователя
    return redirect(url_for('users.get_all_users'))  # Перенаправляем на страницу всех пользователей


# Бан пользователя
@users.route('/ban/<int:user_id>', methods=['POST'])
@token_required
def ban_user(user_id):
    user = User.get_by_id(user_id)
    user.ban_user()  # Баним пользователя
    return redirect(url_for('users.get_all_users'))  # Перенаправляем на страницу всех пользователей


# Разбан пользователя
@users.route('/unban/<int:user_id>', methods=['POST'])
@token_required
def unban_user(user_id):
    user = User.get_by_id(user_id)
    user.unban_user()  # Разбаним пользователя
    return redirect(url_for('users.get_all_users'))  # Перенаправляем на страницу всех пользователей
