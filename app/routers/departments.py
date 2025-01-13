from flask import Blueprint, request, render_template, redirect, url_for, jsonify
from app.db import db, Department, User, UserPermission, Permission, Task
from app.utils import token_required, permission_check

departments = Blueprint('departments', __name__, url_prefix='/departments')

# Просмотр всех департаментов
@departments.route('/', methods=['GET'])
@token_required
def get_all_departments():
    user = request.user

    create = request.cookies.get('perm_create_new_department')
    all_dep = request.cookies.get('perm_view_all_department')
    my_dep = request.cookies.get('perm_view_my_department')
    delete = request.cookies.get('perm_delete_department')

    permission_on_db = Permission.query.filter_by(page='departments').all()
    permission = []
    for item in permission_on_db:
        perm_current = request.cookies.get(f'perm_{item.function}')
        permission.append({item.function: perm_current})
    print(permission)
    result = [

    ]
    departments = Department.query.all()
    for d in departments:
        result.append({
            "id": d.id,
            "name": d.name,
            "description": d.description,
            "icon": d.icon,
            "color": d.color,
            "members": User.query.filter_by(department_id=d.id).count(),
            "all_task": 5,
            "completed_task": 2,
        })
    return render_template('departments/all_departments.html', result=result, user=user, permission=permission)


# Просмотр деталей департамента
@departments.route('/<int:department_id>', methods=['GET'])
@token_required
def get_department_details(department_id):
    user = request.user
    department = Department.get_by_id(department_id)  # Получаем департамент по ID
    return render_template('departments/department-details.html', user=user, department=department)


# Создание департамента
@departments.route('/create', methods=['POST'])
@token_required
def create_department():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        icon = request.form['icon']
        color = request.form['color']

        new_department = Department(name=name, description=description, icon=icon, color=color)
        new_department.save_to_db()  # Сохраняем департамент в базе данных
        return redirect(
            url_for('departments.get_all_departments'))  # Перенаправляем на страницу со всеми департаментами


# Обновление департамента
@departments.route('/update/<int:department_id>', methods=['GET', 'POST'])
@token_required
def update_department(department_id):
    department = Department.get_by_id(department_id)

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        icon = request.form['icon']
        color = request.form['color']

        department.update(name=name, description=description, icon=icon, color=color)  # Обновляем департамент
        return redirect(
            url_for('departments.get_all_departments'))  # Перенаправляем на страницу со всеми департаментами

    return render_template('departments/update_department.html', department=department)


# Удаление департамента
@departments.route('/delete/<int:department_id>', methods=['POST'])
@token_required
def delete_department(department_id):
    department = Department.get_by_id(department_id)
    department.delete()  # Удаляем департамент
    return redirect(url_for('departments.get_all_departments'))  # Перенаправляем на страницу со всеми департаментами
