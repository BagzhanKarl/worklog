from datetime import datetime

from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from app.db import db, Task, Department, Permission, TaskParticipant, TaskFile, TaskComment, DepartmentTaskAssignment, \
    TaskChecklist, TaskPriority, User
from app.routers import departments
from app.utils import token_required, permission_check, generate_unique_id

tasks = Blueprint('tasks', __name__, url_prefix='/tasks')

# Просмотр всех задач
@tasks.route('/')
@token_required
def get_all_tasks():
    user = request.user
    permission_on_db = Permission.query.filter_by(page='tasks').all()
    permission = []
    for item in permission_on_db:
        perm_current = request.cookies.get(f'perm_{item.function}')
        permission.append({item.function: perm_current})

    departments = Department.get_all()
    return render_template('tasks/all-tasks.html',
                    user=user,
                    permission=permission,
                    department=departments
                           )


@tasks.route('/get/<int:department_id>', methods=['POST'])
@token_required
def get_task(department_id):
    user = request.user
    my = False
    my_department = False
    response = []
    if department_id == 0:
        my = True
        tasks = TaskParticipant.query.filter_by(user_id=user['id']).all()
        for task in tasks:
            taskItem = Task.query.filter_by(id=task.task_id).first()
            response.append(
                {
                    'id': taskItem.id,
                    'title': taskItem.title,
                    'task_platform_id': taskItem.platform_id,
                    'members': TaskParticipant.query.filter_by(task_id=task.task_id).count(),
                    'files': TaskFile.query.filter_by(task_id=task.task_id).count(),
                    'comments': TaskComment.query.filter_by(task_id=task.task_id).count(),
                }
            )
    else:
        if user['department_id'] == department_id:
            my_department = True
        my = False
        tasks = DepartmentTaskAssignment.query.filter_by(department_id=department_id).all()
        for task in tasks:
            taskItem = Task.query.filter_by(id=task.task_id).first()
            response.append(
                {
                    'id': taskItem.id,
                    'title': taskItem.title,
                    'task_platform_id': taskItem.platform_id,
                    'members': TaskParticipant.query.filter_by(task_id=task.task_id).count(),
                    'files': TaskFile.query.filter_by(task_id=task.task_id).count(),
                    'comments': TaskComment.query.filter_by(task_id=task.task_id).count(),
                }
            )

    permission_on_db = Permission.query.filter_by(page='tasks').all()
    permission = []
    for item in permission_on_db:
        perm_current = request.cookies.get(f'perm_{item.function}')
        permission.append({item.function: perm_current})

    print(permission)

    return render_template('tasks/task-api-taker.html',
                           user=user,
                           permission=permission,
                           my=my,
                           my_department=my_department,
                           department_id=department_id,
                           tasks=response
                           )


@tasks.route('<string:task_id>', methods=['GET'])
@token_required
def view_task(task_id):
    user = request.user

    task = Task.query.filter_by(platform_id=task_id).first_or_404()

    # Получаем участников задачи
    task_members = TaskParticipant.query.filter_by(task_id=task.id).all()

    # Получаем отделы, связанные с задачей
    dept_assignments = DepartmentTaskAssignment.query.filter_by(task_id=task.id).all()

    # Получаем чек-листы задачи
    checklists = TaskChecklist.query.filter_by(task_id=task.id).all()

    response = {
        "id": task.id,
        "platform_id": task.platform_id,
        "title": task.title,
        "creator": {
            "id": task.creator_id,
            "full_name": User.query.get(task.creator_id).first_name  # Предполагая, что есть модель User
        },
        "priority": task.priority.value,
        "status": task.status.value,
        "created_at": task.created_at,
        "updated_at": task.updated_at.isoformat(),
        "completed_at": task.completed_at if task.completed_at else None,
        "deadline": task.deadline if task.deadline else None,

        "members": {
            "count": len(task_members),
            "members": [{
                "id": member.user_id,
                "full_name": User.query.get(member.user_id).first_name,
                "initials": "".join(word[0].upper() for word in User.query.get(member.user_id).first_name.split()),
                "role": member.role.value,
                "department": Department.query.get(member.department_id).name if member.department_id else None,
                "joined_at": member.joined_at,
                "time_spent": member.time_spent
            } for member in task_members]
        },

        "departments": {
            "count": len(dept_assignments),
            "departments": [{
                "id": dept.department_id,
                "title": Department.query.get(dept.department_id).name,
                "status": dept.status.value,
                "progress": dept.progress,
                "deadline": dept.deadline.isoformat() if dept.deadline else None
            } for dept in dept_assignments]
        },

        "description": task.description,

        "checklists": [{
            "id": checklist.id,
            "title": checklist.title,
            "department_id": checklist.department_id,
            "department_name": Department.query.get(checklist.department_id).name if checklist.department_id else None,
            "created_at": checklist.created_at.isoformat(),
            "items": [{
                "id": item.id,
                "content": item.content,
                "department": Department.query.get(item.department_id).name if item.department_id else None,

                "is_completed": item.is_completed,
                "completed_by": User.query.get(item.completed_by).full_name if item.completed_by else None,
                "completed_at": item.completed_at.isoformat() if item.completed_at else None,
                "weight": item.weight
            } for item in checklist.items.all()]
        } for checklist in checklists],

        "files": {
            "count": task.files.count(),
            "files": [{
                "id": file.id,
                "filename": file.filename,
                "original_filename": file.original_filename,
                "file_type": file.file_type.value,
                "mime_type": file.mime_type,
                "file_size": file.file_size,
                "file_path": file.file_path,
                "uploader": {
                    "id": file.uploader_id,
                    "full_name": User.query.get(file.uploader_id).full_name
                },
                "department_id": file.department_id,
                "uploaded_at": file.uploaded_at.isoformat(),
                "is_deleted": file.is_deleted
            } for file in task.files.filter_by(is_deleted=False)]
        },

        "comments": {
            "count": task.comments.count(),
            "comments": [{
                "id": comment.id,
                "user": {
                    "id": comment.user_id,
                    "full_name": User.query.get(comment.user_id).first_name,
                },
                "department_id": comment.department_id,
                "content": comment.content,
                "created_at": comment.created_at,
                "updated_at": comment.updated_at,
                "files": [{
                    "id": file.id,
                    "filename": file.filename,
                    "original_filename": file.original_filename,
                    "file_type": file.file_type.value,
                    "mime_type": file.mime_type,
                    "file_size": file.file_size,
                    "file_path": file.file_path,
                    "uploaded_at": file.uploaded_at,
                    "is_deleted": file.is_deleted
                } for file in comment.files.filter_by(is_deleted=False)]
            } for comment in task.comments]
        }
    }

    #return jsonify(response)
    print(response)
    # или
    return render_template('tasks/task-details.html', task=response, user=user, now=datetime.now())  # Если нужен HTML шаблон

