from flask import Blueprint, redirect, url_for
from app.db import Role, User, Permission, UserPermission, Shift

install = Blueprint('install', __name__, url_prefix='/install')

istalled = False

@install.route('/start')
def start():
    global istalled
    if istalled:
        return redirect('/')
    else:
        roles_list = [
            {
                'name': 'admin',
                'description': 'Суперпользователь'
            },
            {
                'name': 'head',
                'description': 'Высшие руководство компаний'
            },
            {
                'name': 'ruler',
                'description': 'Руководители отделов'
            },
            {
                'name': 'user',
                'description': 'Сотрудники компаний'
            }
        ]
        for role in roles_list:
            new_role = Role(**role)
            new_role.save_to_db()
        return redirect(url_for('install.user'))

@install.route('/user')
def user():
    global istalled
    user = User(
        first_name='Бағжан',
        second_name='Карл',
        third_name='Бағжан',
        phone='+77761174378',
        job_title='Администратор',
        department_id=None,
        role_id=1,
        shift_id=None,
        is_admin=True,
    )
    user.set_password('12345678')
    user.save_to_db()
    istalled = True
    return redirect(url_for('install.shifts'))

@install.route('/shifts')
def shifts():
    global istalled
    shifts_list = [
        {
            'title': 'Вахта-А',
            'start_day': 1,
            'end_day': 15,
            'is_active': True,
            'itr': False
        },
        {
            'title': 'Вахта-B',
            'start_day': 1,
            'end_day': 15,
            'is_active': True,
            'itr': False
        },
        {
            'title': 'ИТР Вахта-А',
            'start_day': 1,
            'end_day': 15,
            'is_active': True,
            'itr': False
        },
        {
            'title': 'ИТР Вахта-B',
            'start_day': 1,
            'end_day': 15,
            'is_active': True,
            'itr': False
        }
    ]
    for shift in shifts_list:
        new_shift = Shift(**shift)
        new_shift.save_to_db()
    return 'Пока все готова'