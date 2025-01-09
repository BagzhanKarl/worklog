from datetime import datetime

from flask import Blueprint, render_template, redirect
from app.db import Vaxta, Role, Employee, Department, Tasks
from app.routers.main import department

start_bp = Blueprint('start', __name__)
@start_bp.route('/')
def index():
    return render_template('base.html')


@start_bp.route('/first')
def first():
    v1 = Vaxta(
        title='Вахта А (ИТЕР)',
        start_day=1,
        end_day=15,
        is_active=True,
    )
    v2 = Vaxta(
        title='Вахта Б (ИТЕР)',
        start_day=15,
        end_day=30,
        is_active=True,
    )
    v1.save_to_db()
    v2.save_to_db()
    # return redirect('/start/second')

@start_bp.route('/second')
def second():
    role = Role(name='admin')
    role.save_to_db()
    role = Role(name='head')
    role.save_to_db()
    role = Role(name='manager')
    role.save_to_db()
    role = Role(name='user')
    role.save_to_db()
    return redirect('/start/third')

@start_bp.route('/test/task')
def test():

    tasks = [
        Tasks(
            task_platform_id='SDF16',
            title='Разработать функционал для API',
            description='Необходимо реализовать эндпоинты для авторизации',
            priority='high',
            status='new',
            department_id=9,
            deadline=datetime.strptime('20.01.2025', '%d.%m.%Y'),
        ),
        Tasks(
            task_platform_id='SDF17',
            title='Обновить дизайн веб-приложения',
            description='Изменить шапку и добавить новый логотип',
            priority='medium',
            status='inprocess',
            department_id=9,
            deadline=datetime.strptime('22.01.2025', '%d.%m.%Y'),
        ),
        Tasks(
            task_platform_id='SDF18',
            title='Написать тесты для модуля аналитики',
            description='Покрыть unit-тестами новый модуль аналитики',
            priority='low',
            status='testing',
            department_id=9,
            deadline=datetime.strptime('25.01.2025', '%d.%m.%Y'),
        ),
        Tasks(
            task_platform_id='SDF19',
            title='Подготовить отчет по проекту',
            description='Создать финальный отчет для клиента',
            priority='medium',
            status='done',
            department_id=9,
            deadline=datetime.strptime('30.01.2025', '%d.%m.%Y'),
        ),
        Tasks(
            task_platform_id='SDF20',
            title='Настроить CI/CD для проекта',
            description='Добавить автоматическую сборку и деплой',
            priority='high',
            status='new',
            department_id=5,
            deadline=datetime.strptime('15.01.2025', '%d.%m.%Y'),
        ),
    ]

    # Сохраняем задачи в базу данных
    for task in tasks:
        task.save_to_db()

    return 'hello world!'
