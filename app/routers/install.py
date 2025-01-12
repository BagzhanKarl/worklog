from flask import Blueprint, redirect, url_for, jsonify
from app.db import Role, User, Permission, UserPermission, Shift

install = Blueprint('install', __name__, url_prefix='/install')

istalled = False

@install.route('/get/permission')
def get_permission():
    permissions = Permission.query.all()
    response = []
    for permission in permissions:
        response.append({
            'name': permission.name,
            'function': permission.function,
            'description': permission.description,
            'page': permission.page,
            'method': permission.method,
        })

    return jsonify(response)

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
    return redirect(url_for('install.permission'))

@install.route('/permission')
def permission():
    global istalled
    data = [
          {
            "description": "",
            "function": "view_all_shifts",
            "method": 2,
            "name": "Посмотреть все смены",
            "page": "shifts"
          },
          {
            "description": "",
            "function": "view_shifts_itr",
            "method": 2,
            "name": "Посмотреть смены ИТР состава",
            "page": "shifts"
          },
          {
            "description": "",
            "function": "edit_shift",
            "method": 3,
            "name": "Изменить график смены",
            "page": "shifts"
          },
          {
            "description": "",
            "function": "create_new_department",
            "method": 1,
            "name": "Создать новый отдел",
            "page": "departments"
          },
          {
            "description": "",
            "function": "view_all_department",
            "method": 2,
            "name": "Посмотреть все отделы",
            "page": "departments"
          },
          {
            "description": "",
            "function": "view_department",
            "method": 2,
            "name": "Посмотреть свой отдел",
            "page": "departments"
          },
          {
            "description": "",
            "function": "edit_own_department",
            "method": 3,
            "name": "Изменить свой отдел",
            "page": "departments"
          },
          {
            "description": "",
            "function": "edit_all_department",
            "method": 3,
            "name": "Изменить все отделы",
            "page": "departments"
          },
          {
            "description": "",
            "function": "delete_department",
            "method": 4,
            "name": "Удалить отдел",
            "page": "departments"
          },
          {
            "description": "",
            "function": "add_user",
            "method": 1,
            "name": "Добавить сотрудника",
            "page": "users"
          },
          {
            "description": "",
            "function": "view_all_users",
            "method": 2,
            "name": "Посмотреть список сотрудников",
            "page": "users"
          },
          {
            "description": "",
            "function": "view_all_users_on_own_department",
            "method": 2,
            "name": "Посмотреть сотрудники своего отдела",
            "page": "users"
          },
          {
            "description": "",
            "function": "view_profile",
            "method": 2,
            "name": "Посмотреть профиль любого пользователя",
            "page": "users"
          },
          {
            "description": "",
            "function": "view_own_profile",
            "method": 2,
            "name": "Посмотреть свой профиль",
            "page": "users"
          },
          {
            "description": "",
            "function": "edit_other_profiles",
            "method": 3,
            "name": "Изменить других профилей ",
            "page": "users"
          },
          {
            "description": "",
            "function": "edit_own_profile",
            "method": 3,
            "name": "Изменить свой профиль",
            "page": "users"
          },
          {
            "description": "",
            "function": "delete_user",
            "method": 4,
            "name": "Удалить пользователя",
            "page": "users"
          },
          {
            "description": "",
            "function": "create_task_for_own",
            "method": 1,
            "name": "Создать себе задачу",
            "page": "tasks"
          },
          {
            "description": "",
            "function": "create_task_for_own_department",
            "method": 1,
            "name": "Создать задачу для отдела",
            "page": "tasks"
          },
          {
            "description": "",
            "function": "create_task_for_all_departments",
            "method": 1,
            "name": "Создать задачу для всех отделов",
            "page": "tasks"
          },
          {
            "description": "",
            "function": "view_own_tasks",
            "method": 2,
            "name": "Посмотреть свои задачи",
            "page": "tasks"
          },
          {
            "description": "",
            "function": "view_own_department_tasks",
            "method": 2,
            "name": "Просмотр задач собственного отдела",
            "page": "tasks"
          },
          {
            "description": "",
            "function": "view_all_department_tasks",
            "method": 2,
            "name": "Просмотреть задачи всех отделов",
            "page": "tasks"
          },
          {
            "description": "description",
            "function": "update_task_status",
            "method": 3,
            "name": "Изменение статуса задачи",
            "page": "task"
          },
          {
            "description": "description",
            "function": "update_task_priority",
            "method": 3,
            "name": "Изменение приоритета задачи",
            "page": "task"
          },
          {
            "description": "description",
            "function": "add_task_participant",
            "method": 1,
            "name": "Добавление участника задачи",
            "page": "task"
          },
          {
            "description": "description",
            "function": "remove_task_participant",
            "method": 4,
            "name": "Удаление участника задачи",
            "page": "task"
          },
          {
            "description": "description",
            "function": "update_task",
            "method": 3,
            "name": "Редактирование задачи",
            "page": "task"
          },
          {
            "description": "description",
            "function": "archive_task",
            "method": 3,
            "name": "Архивация задачи",
            "page": "task"
          },
          {
            "description": "description",
            "function": "create_checklist",
            "method": 1,
            "name": "Создание чеклиста",
            "page": "task"
          },
          {
            "description": "description",
            "function": "create_checklist_items",
            "method": 1,
            "name": "Создание элементов чеклиста",
            "page": "task"
          },
          {
            "description": "description",
            "function": "uncheck_checklist_items",
            "method": 3,
            "name": "Отмена выполнения элементов чеклиста",
            "page": "task"
          },
          {
            "description": "description",
            "function": "create_comment",
            "method": 1,
            "name": "Добавление комментария",
            "page": "task"
          },
          {
            "description": "description",
            "function": "upload_files",
            "method": 1,
            "name": "Добавление файлов",
            "page": "task"
          },
          {
            "description": "description",
            "function": "delete_files",
            "method": 4,
            "name": "Удаление файлов",
            "page": "task"
          }
        ]

    for item in data:
        permission = Permission(name=item['name'], function=item['function'], description=['description'], page=item['page'], method=item['method'])
        permission.save_to_db()

    return jsonify({'message': 'Permission created successfully'}), 201