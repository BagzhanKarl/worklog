from flask import Blueprint, request, jsonify, render_template, redirect, url_for

from app import db
from app.db import Role, Permission, RolePermission, User, UserPermission
from app.utils import token_required

admin = Blueprint('admin', __name__, url_prefix='/admin')


@admin.route('/update/user/permissions/<int:id>')
@token_required
def update_permissions(id):
    user = User.query.get(id)


########## PERMISSION ##########
@admin.route('/permission', methods=['GET'])
@token_required
def permission_all():
    user = request.user
    return render_template('admin/permission-list.html', user=user)

@admin.route('/permission/roles', methods=['GET', 'POST'])
@token_required
def permission_roles():
    user = request.user
    # Определяем ID ролей
    DIRECTOR_ROLE_ID = 2
    MANAGER_ROLE_ID = 3
    USER_ROLE_ID = 4

    if request.method == 'POST':
        try:
            data = request.form
            permissions = Permission.query.all()
            rules = {}

            # Удаляем старые записи прав
            RolePermission.query.delete()
            db.session.flush()  # Очищаем сессию после удаления

            # Собираем все новые записи для bulk insert
            new_role_permissions = []

            for permission in permissions:
                # Для директора
                director_granted = f'director_{permission.id}' in data
                new_role_permissions.append(
                    RolePermission(
                        permission_id=permission.id,
                        role_id=DIRECTOR_ROLE_ID,
                        is_granted=director_granted
                    )
                )

                # Для руководителя
                manager_granted = f'manager_{permission.id}' in data
                new_role_permissions.append(
                    RolePermission(
                        permission_id=permission.id,
                        role_id=MANAGER_ROLE_ID,
                        is_granted=manager_granted
                    )
                )

                # Для пользователя
                user_granted = f'user_{permission.id}' in data
                new_role_permissions.append(
                    RolePermission(
                        permission_id=permission.id,
                        role_id=USER_ROLE_ID,
                        is_granted=user_granted
                    )
                )

                rules[permission.name] = {
                    'rule': permission.id,
                    'head': director_granted,
                    'ruler': manager_granted,
                    'user': user_granted
                }

            # Добавляем все новые записи одним запросом
            db.session.bulk_save_objects(new_role_permissions)
            db.session.commit()

            return redirect(url_for('admin.permission_roles'))

        except Exception as e:
            db.session.rollback()
            return redirect(url_for('admin.permission_roles'))

    else:
        try:
            permissions = Permission.query.order_by(Permission.id).all()
            response = []

            # Получаем все права ролей для всех разрешений одним запросом
            role_permissions = RolePermission.query.filter(
                RolePermission.role_id.in_([DIRECTOR_ROLE_ID, MANAGER_ROLE_ID, USER_ROLE_ID])
            ).all()

            # Создаем словарь для быстрого доступа к правам
            role_permissions_dict = {
                (rp.permission_id, rp.role_id): rp.is_granted
                for rp in role_permissions
            }

            for permission in permissions:
                response.append({
                    'id': permission.id,
                    'name': permission.name,
                    'director': role_permissions_dict.get((permission.id, DIRECTOR_ROLE_ID), False),
                    'manager': role_permissions_dict.get((permission.id, MANAGER_ROLE_ID), False),
                    'user': role_permissions_dict.get((permission.id, USER_ROLE_ID), False),
                })

            return render_template('admin/permission-roles.html', user=user, permissions=response)

        except Exception as e:
            return redirect(url_for('admin.dashboard'))  # или другой подходящий маршрут


# Получить все разрешения
@admin.route('/permissions', methods=['GET'])
def get_permissions():
    permissions = Permission.get_all()
    return jsonify([{
        'id': perm.id,
        'name': perm.name,
        'function': perm.function,
        'description': perm.description
    } for perm in permissions])

@admin.route('/permissions/add', methods=['GET', 'POST'])
@token_required
def add_permission():
    user = request.user
    if request.method == 'POST':
        name = request.form['name']
        function = request.form['function']
        description = request.form.get('description')
        page=request.form.get('page')
        method=request.form.get('method')
        permission = Permission(
            name=name,
            function=function,
            description=description,
            page=page,
            method=method,
        )
        permission.save_to_db()
        return redirect(url_for('admin.add_permission'))
    else:
        return render_template('admin/permission-add.html', user=user)

# Создать разрешение
@admin.route('/permissions', methods=['POST'])
def create_permission():
    data = request.get_json()
    name = data.get('name')
    function = data.get('function')
    description = data.get('description')

    if not name or not function:
        return jsonify({'message': 'Name and Function are required'}), 400

    permission = Permission(name=name, function=function, description=description)
    permission.save_to_db()

    return jsonify({'message': 'Permission created successfully'}), 201

# Создать разрешение по массиву
@admin.route('/permissions/list/create', methods=['GET'])
def create_permission_array():
    data = [
        {
            "name": "Изменение статуса задачи",
            "function": "update_task_status",
            "description": "Позволяет изменять текущий статус задачи на другой доступный статус",
            "page": "task",
            "method": 3
        },
        {
            "name": "Изменение приоритета задачи",
            "function": "update_task_priority",
            "description": "Позволяет изменять уровень приоритета выполнения задачи",
            "page": "task",
            "method": 3
        },
        {
            "name": "Добавление участника задачи",
            "function": "add_task_participant",
            "description": "Позволяет добавлять новых участников к существующей задаче",
            "page": "task",
            "method": 1
        },
        {
            "name": "Удаление участника задачи",
            "function": "remove_task_participant",
            "description": "Позволяет удалять существующих участников из задачи",
            "page": "task",
            "method": 4
        },
        {
            "name": "Редактирование задачи",
            "function": "update_task",
            "description": "Позволяет изменять основную информацию задачи (название, описание, сроки и др.)",
            "page": "task",
            "method": 3
        },
        {
            "name": "Архивация задачи",
            "function": "archive_task",
            "description": "Позволяет перемещать задачу в архив",
            "page": "task",
            "method": 3
        },
        {
            "name": "Создание чеклиста",
            "function": "create_checklist",
            "description": "Позволяет создавать новый чеклист в задаче",
            "page": "task",
            "method": 1
        },
        {
            "name": "Создание элементов чеклиста",
            "function": "create_checklist_items",
            "description": "Позволяет добавлять новые элементы в существующий чеклист",
            "page": "task",
            "method": 1
        },
        {
            "name": "Отмена выполнения элементов чеклиста",
            "function": "uncheck_checklist_items",
            "description": "Позволяет отменять отметку о выполнении элементов чеклиста",
            "page": "task",
            "method": 3
        },
        {
            "name": "Добавление комментария",
            "function": "create_comment",
            "description": "Позволяет создавать новые комментарии к задаче",
            "page": "task",
            "method": 1
        },
        {
            "name": "Добавление файлов",
            "function": "upload_files",
            "description": "Позволяет загружать файлы к задаче",
            "page": "task",
            "method": 1
        },
        {
            "name": "Удаление файлов",
            "function": "delete_files",
            "description": "Позволяет удалять прикрепленные к задаче файлы",
            "page": "task",
            "method": 4
        }
    ]

    for item in data:
        permission = Permission(name=item['name'], function=item['function'], description=['description'], page=item['page'], method=item['method'])
        permission.save_to_db()

    return jsonify({'message': 'Permission created successfully'}), 201


########## ROLES ##########
# Получить все роли
@admin.route('/roles', methods=['GET'])
def get_roles():
    roles = Role.get_all()
    return jsonify([role.name for role in roles])

# Получить роль по ID
@admin.route('/roles/<int:role_id>', methods=['GET'])
def get_role_by_id(role_id):
    role = Role.get_by_id(role_id)
    if role:
        return jsonify({'id': role.id, 'name': role.name, 'description': role.description})
    return jsonify({'message': 'Role not found'}), 404

# Создать роль
@admin.route('/roles', methods=['POST'])
def create_role():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')

    if not name:
        return jsonify({'message': 'Name is required'}), 400

    role = Role(name=name, description=description)
    role.save_to_db()

    return jsonify({'message': 'Role created successfully'}), 201

# Обновить роль
@admin.route('/roles/<int:role_id>', methods=['PUT'])
def update_role(role_id):
    role = Role.get_by_id(role_id)
    if not role:
        return jsonify({'message': 'Role not found'}), 404

    data = request.get_json()
    name = data.get('name')
    description = data.get('description')

    role.update(name=name, description=description)

    return jsonify({'message': 'Role updated successfully'}), 200

# Удалить роль
@admin.route('/roles/<int:role_id>', methods=['DELETE'])
def delete_role(role_id):
    role = Role.get_by_id(role_id)
    if not role:
        return jsonify({'message': 'Role not found'}), 404

    role.delete()

    return jsonify({'message': 'Role deleted successfully'}), 200