from flask import Blueprint, request, render_template, redirect, url_for
from app.db import db, User, Department, Shift, Role, Permission, ShiftPerson
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
    user = request.user
    userDetails = User.get_by_id(user_id)  # Получаем пользователя по ID
    permission_on_db = Permission.query.filter_by(page='users').all()
    permission = []
    response = {
        "id": userDetails.id,
        "first_name": userDetails.first_name,
        "second_name": userDetails.second_name,
        "third_name": userDetails.third_name,
        "phone": userDetails.phone,
        "job_title": userDetails.job_title,
        "initials": userDetails.first_name[0].upper() + userDetails.second_name[0].upper(),
        "shift_id": userDetails.shift_id,
        "shift": str(Shift.query.filter_by(id=userDetails.shift_id).first().start_day) + "-" + str(Shift.query.filter_by(id=userDetails.department_id).first().end_day) + " число",
        "shift_list": [{
            "id": shift.id,
            "name": shift.title,
        }for shift in Shift.get_all()],
        "department_id": userDetails.department_id,
        "department": Department.query.filter_by(id=userDetails.department_id).first().name,
        "department_list": [{
            "id": department.id,
            "name": department.name
        }  for department in Department.query.all()],
        "role_id": userDetails.role_id,
        "role_list": [{
            "id": role.id,
            "name": role.name
        } for role in Role.query.all()],
    }
    for item in permission_on_db:
        perm_current = request.cookies.get(f'perm_{item.function}')
        permission.append({item.function: perm_current})
    partic = User.query.all()
    return render_template('users/user_details.html', partic=partic, user=user, userDetails=response, permission=permission)


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
@users.route('/<int:user_id>/update', methods=['GET', 'POST'])
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

        if ShiftPerson.query.filter_by(first_user=user_id).first() or ShiftPerson.query.filter_by(second_user=user_id).first():
            if ShiftPerson.query.filter_by(first_user=user_id).first():
                data = ShiftPerson.query.filter_by(first_user=user_id).first()
                data.second_user = request.form.get('shift_user_id')
            elif Shift.query.filter_by(second_user=user_id).first():
                data = Shift.query.filter_by(second_user=user_id).first()
                data.first_user = request.form.get('shift_user_id')
            db.session.commit()
        else:
            user = ShiftPerson(
                first_user=user_id,
                second_user=request.form.get('shift_user_id'),
            )
            db.session.add(user)
            db.session.commit()

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

