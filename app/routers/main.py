from calendar import monthrange
from datetime import datetime
import math
from flask import Blueprint, request, redirect, render_template, url_for, jsonify
from sqlalchemy import func

from app import db
from app.db import Vaxta, Employee, Department, Role, Tasks
from app.utils import hash_password
from app.utils.jwttoken import token_required

main = Blueprint('main', __name__)

@main.route('/')
@token_required
def index():
    user = request.user
    return render_template('main/index.html', user=user)


from flask import redirect, url_for, flash


@main.route('/shifts', methods=['GET', 'POST'])
@token_required
def shifts():
    if request.method == 'POST':
        check = request.user
        if check['role_id'] == 1 or check['role_id'] == 2:
            # Получаем все данные из формы
            form_data = request.form

            # Обновляем каждую вахту
            for key, value in form_data.items():
                if key.startswith('v') and key[1:].isdigit():
                    shift_id = int(key[1:])  # Извлекаем ID из имени поля

                    # Получаем объект вахты из базы данных
                    vaxta = Vaxta.query.filter_by(id=shift_id).first()
                    if vaxta:
                        vaxta.title = value  # Обновляем название
                        vaxta.start_day = int(form_data.get(f"startv{shift_id}", vaxta.start_day))
                        vaxta.end_day = int(form_data.get(f"endv{shift_id}", vaxta.end_day))

            # Сохраняем все изменения
            db.session.commit()
            flash('Изменения успешно сохранены!', 'success')

            # Перенаправляем на GET-запрос
            return redirect(url_for('main.shifts'))
        else:
            return redirect(url_for('main.no_rights'))

    # GET-запрос: формируем данные для отображения
    vaxta_list = Vaxta.query.all()
    today = datetime.now()
    current_day = today.day
    last_day_of_month = monthrange(today.year, today.month)[1]
    shifts = []

    for vaxta in vaxta_list:
        # Проверяем активность вахты
        if vaxta.start_day <= vaxta.end_day:  # Обычная вахта в пределах одного месяца
            vaxta.is_active = vaxta.start_day <= current_day <= vaxta.end_day
        else:  # Вахта, переходящая через границу месяца
            vaxta.is_active = current_day >= vaxta.start_day or current_day <= vaxta.end_day

        # Подсчитываем количество пользователей
        user_count = db.session.query(func.count(Employee.id)).filter(Employee.vaxta_id == vaxta.id).scalar()

        shifts.append({
            'id': vaxta.id,
            'title': vaxta.title,
            'start_day': vaxta.start_day,
            'end_day': vaxta.end_day,
            'active': vaxta.is_active,
            'count': user_count,
            'iter': vaxta.iter,
        })

    # Сохраняем изменения статуса активности
    db.session.commit()

    # Отправляем данные в шаблон
    user = request.user
    return render_template('main/shifts.html', user=user, shifts=shifts)


@main.route('/departments', methods=['GET', 'POST'])
@token_required
def departments():
    user = request.user
    if request.method == 'POST':
        if user['role_id'] == 1 or user['role_id'] == 2:
            title = request.form.get('name')
            description = request.form.get('description')
            icon = request.form.get('icon')
            color = request.form.get('color')
            dep = Department(name=title, description=description, icon=icon, color=color)
            dep.save_to_db()
            return redirect(url_for('main.departments'))
        else:
            return redirect(url_for('main.no_rights'))
    else:
        list = Department.query.all()
        result = []
        for d in list:
            userCount = Employee.query.filter_by(department_id=d.id).count()
            comp = math.ceil((15 / 68) * 100)
            result.append({
                'id': d.id,
                'name': d.name,
                'description': d.description,
                'icon': d.icon,
                'color': d.color,
                'all_task': 68,
                'completed': 15,
                'pers': comp,
                'users': userCount,
            })
        return render_template('main/departments.html',user=user, result=result)

@main.route('/department/<int:id>')
@token_required
def department(id):
    user = request.user
    department = Department.query.get_or_404(id)
    comp = math.ceil((15 / 68) * 100)
    userCount = Employee.query.filter_by(department_id=department.id).order_by(Employee.role_id).all()
    user_list = []
    for item in userCount:
        initials = item.first_name[0].upper() + item.second_name[0].upper()
        user_list.append({
            'initials': initials,
            'name': f'{item.second_name} {item.first_name} {item.third_name}',
            'role': item.job_title
        })
    dep = {
        'id': department.id,
        'name': department.name,
        'description': department.description,
        'icon': department.icon,
        'color': department.color,
        'all_task': 68,
        'completed': 15,
        'pers': comp,
        'users': len(userCount),
        'members': user_list
    }
    return render_template('main/department_detail.html', user=user, department=dep)


@main.route('/users')
@token_required
def users():
    user = request.user
    return render_template('main/users.html', user=user)

@main.route('/tasks')
@token_required
def tasks():
    user = request.user
    department = Department.query.all()
    return render_template('main/tasks.html', user=user, department=department)

@main.route('/task/<string:id>', methods=['GET'])
@token_required
def task(id):
    user = request.user
    task = Tasks.query.filter_by(task_platform_id=id).first()
    return render_template('main/task-details.html', user=user, task=task)


########### COMPLETED ###########

@main.route('/add/new/employe', methods=['GET', 'POST'])
@token_required
def add_employee():
    if request.method == 'POST':
        user = request.user
        form_data = request.form
        first_name = form_data.get('first_name')
        second_name = form_data.get('last_name')
        third_name = form_data.get('middle_name')
        job_title = form_data.get('position')
        phone = form_data.get('phone')
        password = form_data.get('password')

        department = int(form_data.get('department'))
        vaxta = int(form_data.get('shift'))
        role = int(form_data.get('role'))

        new_user = Employee(
            first_name=first_name,
            second_name=second_name,
            third_name=third_name,
            job_title=job_title,
            phone=phone,
            password=hash_password(password),
            department_id=department,
            vaxta_id=vaxta,
            role_id=role,
        )
        new_user.save_to_db()
        dep = request.args.get('dep')
        return redirect(url_for('main.department', id=dep))
    else:
        user = request.user
        deplist = []
        departments = Department.query.all()
        for d in departments:
            deplist.append({
                "id": d.id,
                "name": d.name,
            })
        vaxta_list = []
        vaxta = Vaxta.query.all()
        for vaxta in vaxta:
            vaxta_list.append({
                "id": vaxta.id,
                "title": vaxta.title,
            })
        role_list = []
        roles = Role.query.all()
        for role in roles:
            role_list.append({
                'id': role.id,
                "name": role.name,
            })
        dep = request.args.get('dep')  # Получаем параметр 'dep' из строки запроса
        if dep:
            return render_template('user/add-new-user.html', user=user, role=role_list, departments=deplist, vaxta=vaxta_list, dep=int(dep))
        else:
            return redirect(url_for('main.departments'))

@main.route('/department/<int:id>/delete', methods=['GET'])
@token_required
def department_delete(id):
    user = request.user
    if user['role_id'] == 1 or user['role_id'] == 2:
        department = Department.query.get(id)
        if department:
            db.session.delete(department)
            db.session.commit()
            return redirect(url_for('main.departments'))
        else: return redirect(url_for('main.no_rights'))
    else:
        return redirect(url_for('main.no_rights'))

@main.route('/no-rights', methods=['GET'])
@token_required
def no_rights():
    user = request.user
    return render_template('errors/403.html', user=user)