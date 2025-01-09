from flask import Blueprint, request, jsonify

from app.db import Tasks, File
from app.utils import save_file
from app.utils.jwttoken import token_required

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/tasks/department/<int:id>', methods=['POST'])
@token_required
def tast_department(id):
    tasks = Tasks.query.filter_by(department_id=id).all()
    response = []
    for task in tasks:
        response.append({
            'id': task.id,
            'platform_id': task.task_platform_id,
            'title': task.title,
            'description': task.description,
            'priority': task.priority,
            'status': task.status,
            'department_id': task.department_id,
            'deadline': task.deadline,
            'created_at': task.created_at,
            'updated_at': task.updated_at,
        })

    return jsonify(response)

@api.route('/add/comment/<int:id>', methods=['POST'])
@token_required
def add_comment(id):
    user = request.user
    comment = request.form.get('comment', '').strip()
    file = request.files.get('file')
    file_result = None
    if file and file.filename:
        file_result = save_file(file)

    if file_result:
        file_db = File(
            task_id=id,
            file_url=file_result.file_path,
            original_file_name=file_result.original_filename,
            uploaded_by=user['id']
        )
        file_db.save_to_db()

    response = {
        "message": "Комментарий добавлен успешно",
        "data": {
            "task_id": id,
            "comment": comment,
            "file": file_result  # Вернёт None, если файла не было
        }
    }
    return jsonify(response), 200
