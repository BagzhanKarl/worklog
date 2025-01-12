from flask import Blueprint, request, jsonify, redirect, url_for
from app.db import db, Department, TaskPriority, TaskStatus, User, FileType
from datetime import datetime
from app.db import (
    Task, TaskParticipant, TaskChecklist, ChecklistItem,
    TaskFile, CommentFile, TaskComment, DepartmentTaskAssignment
)
import os
import uuid
from werkzeug.utils import secure_filename
from datetime import datetime

from app.utils import generate_unique_id, token_required

# Создаем Blueprint для API, который будет использоваться для маршрутов
api = Blueprint('api', __name__, url_prefix='/api')

# Класс для работы с файлами
class FileHandler:
    def __init__(self, base_upload_path):
        # Инициализируем базовый путь для загрузки файлов
        self.base_upload_path = base_upload_path

    def _create_unique_filename(self, original_filename):
        """Создает уникальное имя файла"""
        ext = os.path.splitext(original_filename)[1]  # Получаем расширение файла
        return f"{uuid.uuid4().hex}{ext}"  # Создаем уникальное имя на основе UUID

    def _get_year_month_path(self):
        """Создает путь year/month для организации файлов"""
        now = datetime.now()  # Получаем текущую дату
        return os.path.join(str(now.year), str(now.month).zfill(2))  # Формируем путь

    def save_file(self, file, subdir='general'):
        """
        Сохраняет файл и возвращает информацию о нем

        Args:
            file: FileStorage object
            subdir: подпапка для организации файлов (например, 'tasks', 'comments')

        Returns:
            dict с информацией о сохраненном файле
        """
        secure_original = secure_filename(file.filename)  # Обеспечиваем безопасное имя файла
        unique_filename = self._create_unique_filename(secure_original)  # Генерируем уникальное имя файла

        # Формируем путь для сохранения файла
        year_month = self._get_year_month_path()
        relative_path = os.path.join(subdir, year_month)
        full_path = os.path.join(self.base_upload_path, relative_path)

        # Создаем директории, если их нет
        os.makedirs(full_path, exist_ok=True)

        file_full_path = os.path.join(full_path, unique_filename)  # Полный путь к файлу
        relative_file_path = os.path.join(relative_path, unique_filename)  # Относительный путь

        file.seek(0)  # Возвращаем указатель файла в начало
        file.save(file_full_path)  # Сохраняем файл на диск

        return {
            'filename': unique_filename,
            'original_filename': secure_original,
            'relative_path': relative_file_path,
            'full_path': file_full_path,
            'file_size': os.path.getsize(file_full_path)  # Получаем размер файла
        }

    def delete_file(self, file_path):
        """Удаляет файл"""
        full_path = os.path.join(self.base_upload_path, file_path)  # Полный путь к файлу
        if os.path.exists(full_path):  # Проверяем существование файла
            os.remove(full_path)  # Удаляем файл
            return True
        return False

# Инициализируем обработчик файлов
file_handler = FileHandler(os.getenv('UPLOAD_PATH', 'uploads'))

# Создание задачи
@api.route('/tasks', methods=['POST'])
@token_required
def create_task():
    if not request.user or 'id' not in request.user:
        return jsonify({'error': 'User not found'}), 401

    user = request.user

    try:
        # Проверка и получение обязательных полей
        if 'title' not in request.form:
            return jsonify({'error': 'Title is required'}), 400

        title = request.form['title']
        description = request.form.get('desc')

        # Валидация priority
        priority = request.form.get('priority')
        if not priority or priority not in [p.value for p in TaskPriority]:
            return jsonify({'error': 'Invalid priority value'}), 400

        # Валидация status
        status = request.form.get('status', 'new')
        if status not in [s.value for s in TaskStatus]:
            return jsonify({'error': 'Invalid status value'}), 400

        # Безопасное получение deadline
        deadline = None
        if deadline_str := request.form.get('deadline'):
            try:
                deadline = datetime.fromisoformat(deadline_str)
            except ValueError:
                return jsonify({'error': 'Invalid deadline format'}), 400

        # Безопасное получение department_id
        department_id = request.form.get('department_id', type=int)
        if department_id is None:
            return jsonify({'error': 'Department ID is required'}), 400

        # Проверка существования департамента если id не 0
        if department_id != 0:
            department = Department.query.get(department_id)
            if not department:
                return jsonify({'error': 'Department not found'}), 404

        # Создаем задачу
        task = Task(
            platform_id=generate_unique_id(),
            title=title,
            description=description,
            priority=priority,
            status=status,
            deadline=deadline,
            creator_id=user['id']
        )

        db.session.add(task)
        db.session.commit()

        # Добавляем связи в зависимости от department_id
        if department_id == 0:
            participant = TaskParticipant(
                task_id=task.id,
                user_id=user['id'],
                department_id=None,  # Явно указываем None
                role='admin'
            )
            db.session.add(participant)
        else:
            assignment = DepartmentTaskAssignment(
                task_id=task.id,
                department_id=department_id,
                status='new',
                progress=0
            )
            participant = TaskParticipant(
                task_id=task.id,
                user_id=user['id'],
                department_id=department_id,  # Явно указываем None
                role='admin'
            )
            db.session.add(participant)
            db.session.add(assignment)

        db.session.commit()

        return redirect(url_for('tasks.get_all_tasks'))

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@api.route('/task/<int:task_id>/update', methods=['POST'])
@token_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)

    try:
        # Получаем данные из формы
        title = request.form.get('title')
        description = request.form.get('description')
        priority = request.form.get('priority')
        deadline_str = request.form.get('deadline')

        # Валидация обязательных полей
        if not title:
            return redirect(url_for('tasks.view_task', task_id=task_id))

        if not priority or priority not in ['urgent', 'high', 'medium', 'low']:
            return redirect(url_for('tasks.view_task', task_id=task_id))

        # Обновляем данные задачи
        task.title = title
        task.description = description
        task.priority = TaskPriority[priority.upper()]

        # Обрабатываем дедлайн
        if deadline_str:
            try:
                task.deadline = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                return redirect(url_for('tasks.view_task', task_id=task.platform_id))
        else:
            task.deadline = None

        db.session.commit()

        # Перенаправляем на страницу задачи
        return redirect(url_for('tasks.view_task', task_id=task.platform_id))

    except Exception as e:
        db.session.rollback()
        return redirect(url_for('tasks.view_task', task_id=task.platform_id))


@api.route('/task/<int:task_id>/members/add', methods=['POST'])
@token_required
def add_task_member(task_id):
    task = Task.query.get_or_404(task_id)

    try:
        user_id = request.form.get('user_id', type=int)
        role = request.form.get('role')

        # Валидация входных данных
        if not user_id:
            return redirect(url_for('tasks.view_task', task_id=task.platform_id))

        if not role or role not in ['responsible', 'executor', 'observer']:
            return redirect(url_for('tasks.view_task', task_id=task.platform_id))

        # Проверяем, не является ли пользователь уже участником
        existing = TaskParticipant.query.filter_by(
            task_id=task_id,
            user_id=user_id
        ).first()

        if existing:
            return redirect(url_for('tasks.view_task', task_id=task.platform_id))

        # Создаем нового участника
        participant = TaskParticipant(
            task_id=task_id,
            user_id=user_id,
            role=role
        )

        db.session.add(participant)
        db.session.commit()

        return redirect(url_for('tasks.view_task', task_id=task.platform_id))

    except Exception as e:
        db.session.rollback()
        return redirect(url_for('tasks.view_task', task_id=task.platform_id))


@api.route('/task/<int:task_id>/checklist/add', methods=['POST'])
@token_required
def add_task_checklist(task_id):
    task = Task.query.get_or_404(task_id)

    try:
        # Получаем данные из формы
        title = request.form.get('title')
        department_id = request.form.get('department_id', type=int)

        # Валидация названия
        if not title:
            return redirect(url_for('tasks.view_task', task_id=task.platform_id))

        # Проверяем существование отдела, если он указан
        if department_id:
            department = Department.query.get(department_id)
            if not department:
                return redirect(url_for('tasks.view_task', task_id=task.platform_id))

        # Создаем чек-лист
        checklist = TaskChecklist(
            task_id=task_id,
            title=title,
            department_id=department_id if department_id else None
        )

        db.session.add(checklist)
        db.session.commit()

        return redirect(url_for('tasks.view_task', task_id=task.platform_id))

    except Exception as e:
        db.session.rollback()
        return redirect(url_for('tasks.view_task', task_id=task.platform_id))


@api.route('/task/<int:task_id>/checklist/add/item', methods=['POST'])
@token_required
def add_checklist_item(task_id):
    try:
        task = Task.query.get_or_404(task_id)

        # Получаем данные из формы
        checklist_id = request.form.get('checklist_id', type=int)
        content = request.form.get('content')

        # Проверяем существование чек-листа и его привязку к задаче
        checklist = TaskChecklist.query.filter_by(
            id=checklist_id,
            task_id=task_id
        ).first_or_404()

        # Валидация контента
        if not content:
            return redirect(url_for('tasks.view_task', task_id=task.platform_id))

        # Создаем элемент чек-листа
        checklist_item = ChecklistItem(
            checklist_id=checklist_id,
            content=content,
            weight=1,  # Дефолтный вес
            department_id=checklist.department_id  # Наследуем отдел от чек-листа
        )

        db.session.add(checklist_item)
        db.session.commit()

        return redirect(url_for('tasks.view_task', task_id=task.platform_id))

    except Exception as e:
        db.session.rollback()
        return redirect(url_for('tasks.view_task', task_id=task.platform_id))


@api.route('/task/<int:task_id>/archive', methods=['POST'])
@token_required
def archive_task(task_id):
    task = Task.query.get_or_404(task_id)

    try:
        # Получаем причину архивации
        archive_reason = request.form.get('archive_reason')

        # Валидация причины
        if not archive_reason:
            return redirect(url_for('tasks.view_task', task_id=task.platform_id))

        # Меняем статус задачи на ARCHIVED
        task.status = TaskStatus.ARCHIVED

        # Также архивируем все назначения на отделы
        dept_assignments = DepartmentTaskAssignment.query.filter_by(task_id=task_id).all()
        for assignment in dept_assignments:
            assignment.status = TaskStatus.ARCHIVED

        # Здесь можно добавить логику для отправки уведомлений участникам
        # for participant in task.participants:
        #     send_notification(participant.user_id, 'task_archived', {
        #         'task_id': task.id,
        #         'task_title': task.title,
        #         'archive_reason': archive_reason
        #     })

        db.session.commit()

        return redirect(url_for('tasks.view_task', task_id=task.platform_id))

    except Exception as e:
        db.session.rollback()
        return redirect(url_for('tasks.view_task', task_id=task.platform_id))


@api.route('/task/<int:task_id>/comment/add', methods=['POST'])
@token_required
def add_comment(task_id):
    task = Task.query.get_or_404(task_id)

    try:
        # Получаем текст комментария
        content = request.form.get('content')
        if not content:
            return jsonify({'error': 'Текст комментария обязателен'}), 400

        # Создаем комментарий
        comment = TaskComment(
            task_id=task_id,
            user_id=request.user['id'],
            content=content
        )
        db.session.add(comment)
        db.session.commit()  # Сначала сохраняем комментарий чтобы получить его id

        # Обрабатываем прикрепленные файлы
        files = request.files.getlist('files')
        for file in files:
            if file and file.filename:
                try:
                    # Проверяем расширение файла
                    filename = file.filename.lower()
                    if not any(filename.endswith(ext) for ext in
                               ['.pdf', '.doc', '.docx', '.xls', '.xlsx',
                                '.jpg', '.jpeg', '.png', '.zip', '.rar']):
                        continue

                    # Сохраняем файл
                    file_info = file_handler.save_file(file, subdir='comments')

                    # Определяем тип файла
                    ext = os.path.splitext(filename)[1]
                    if ext in ['.jpg', '.jpeg', '.png']:
                        file_type = 'image'
                    elif ext in ['.zip', '.rar']:
                        file_type = 'archive'
                    elif ext in ['.pdf', '.doc', '.docx']:
                        file_type = 'document'
                    elif ext in ['.xls', '.xlsx']:
                        file_type = 'document'
                    else:
                        file_type = 'other'

                    # Создаем запись о файле
                    comment_file = CommentFile(
                        comment_id=comment.id,
                        uploader_id=request.user['id'],
                        filename=file_info['filename'],
                        original_filename=file_info['original_filename'],
                        file_type=file_type,
                        mime_type=file.content_type,
                        file_size=file_info['file_size'],
                        file_path=file_info['relative_path']
                    )
                    db.session.add(comment_file)
                except Exception as e:
                    # В случае ошибки с файлом пропускаем его и продолжаем
                    continue

        db.session.commit()
        return redirect(url_for('tasks.view_task', task_id=task.platform_id))

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@api.route('/tasks/checkitem/completed/<int:item_id>', methods=['POST'])
@token_required
def toggle_checklist_item(item_id):
    item = ChecklistItem.query.get_or_404(item_id)

    try:
        # Получаем новый статус из запроса
        is_completed = request.form.get('completed', '').lower() == 'true'

        # Обновляем статус элемента
        item.is_completed = is_completed

        # Если задача отмечена как выполненная
        if is_completed:
            item.completed_by = request.user['id']
            item.completed_at = datetime.now()

            # Получаем информацию о пользователе для ответа
            user = User.query.get(request.user['id'])
            completed_by = user.first_name + " " + user.second_name if user else ''

            response_data = {
                'completed_by': completed_by,
                'completed_at': item.completed_at.strftime('%d.%m.%Y %H:%M')
            }
        else:
            # Если задача снята с выполнения, очищаем информацию
            item.completed_by = None
            item.completed_at = None
            response_data = {
                'completed_by': None,
                'completed_at': None
            }

        db.session.commit()
        return jsonify(response_data)

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@api.route('/tasks/<int:task_id>/changestatus', methods=['POST'])
@token_required
def change_task_status(task_id):
    task = Task.query.get_or_404(task_id)

    try:
        # Получаем новый статус из запроса
        new_status = request.form.get('status')

        if not new_status:
            return jsonify({
                'message': 'Статус не указан'
            }), 400

        if new_status not in [status.value for status in TaskStatus]:
            return jsonify({
                'message': 'Некорректный статус'
            }), 400

        # Обновляем статус задачи
        task.status = TaskStatus(new_status)

        # Если статус изменен на "completed", устанавливаем время завершения
        if new_status == TaskStatus.COMPLETED.value:
            task.completed_at = datetime.now()

        # Обновляем время изменения
        task.updated_at = datetime.now()

        db.session.commit()

        return jsonify({
            'message': 'Статус успешно обновлен',
            'status': new_status,
            'status_updated_at': task.updated_at.isoformat()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'message': 'Произошла ошибка при обновлении статуса',
            'error': str(e)
        }), 400


@api.route('/tasks/<int:task_id>/change/priority', methods=['POST'])
@token_required
def change_task_priority(task_id):
    task = Task.query.get_or_404(task_id)

    try:
        # Получаем новый приоритет из запроса
        new_priority = request.form.get('priority')

        if not new_priority:
            return jsonify({
                'message': 'Приоритет не указан'
            }), 400

        # Проверяем, что приоритет имеет допустимое значение
        if new_priority not in [priority.value for priority in TaskPriority]:
            return jsonify({
                'message': 'Некорректный приоритет'
            }), 400

        # Обновляем приоритет задачи
        task.priority = TaskPriority(new_priority)
        task.updated_at = datetime.now()

        db.session.commit()

        return jsonify({
            'message': 'Приоритет успешно обновлен',
            'priority': new_priority,
            'updated_at': task.updated_at.isoformat()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'message': 'Произошла ошибка при обновлении приоритета',
            'error': str(e)
        }), 400


@api.route('/task/<int:task_id>/upload', methods=['POST'])
@token_required
def upload_task_files(task_id):
    task = Task.query.get_or_404(task_id)

    try:
        if 'files[]' not in request.files:
            return jsonify({
                'message': 'Файлы не были загружены'
            }), 400

        files = request.files.getlist('files[]')

        # Проверяем, что есть хотя бы один файл
        if not files or all(not file.filename for file in files):
            return jsonify({
                'message': 'Не выбрано ни одного файла'
            }), 400

        uploaded_files = []
        errors = []

        for file in files:
            if file and file.filename:
                try:
                    # Проверяем размер файла (50 MB = 52428800 bytes)
                    if len(file.read()) > 52428800:
                        errors.append(f'Файл {file.filename} превышает максимальный размер в 50 MB')
                        file.seek(0)
                        continue

                    file.seek(0)
                    file_info = file_handler.save_file(file, subdir='tasks')

                    # Определяем тип файла на основе расширения
                    ext = os.path.splitext(file.filename.lower())[1]
                    if ext in ['.jpg', '.jpeg', '.png', '.gif']:
                        file_type = FileType.IMAGE
                    elif ext in ['.pdf', '.doc', '.docx']:
                        file_type = FileType.DOCUMENT
                    elif ext in ['.zip', '.rar', '.7z']:
                        file_type = FileType.ARCHIVE
                    else:
                        file_type = FileType.OTHER

                    task_file = TaskFile(
                        task_id=task_id,
                        uploader_id=request.user['id'],
                        filename=file_info['filename'],
                        original_filename=file_info['original_filename'],
                        file_type=file_type,
                        mime_type=file.content_type,
                        file_size=file_info['file_size'],
                        file_path=file_info['relative_path']
                    )

                    db.session.add(task_file)
                    uploaded_files.append({
                        'original_name': file.filename,
                        'size': file_info['file_size']
                    })

                except Exception as e:
                    errors.append(f'Ошибка при загрузке файла {file.filename}: {str(e)}')
                    continue

        if uploaded_files:
            db.session.commit()

        response = {
            'message': f'Успешно загружено файлов: {len(uploaded_files)}',
            'uploaded_files': uploaded_files
        }

        if errors:
            response['errors'] = errors

        # Возвращаем 207 Multi-Status если есть и успешные загрузки, и ошибки
        status_code = 207 if errors and uploaded_files else 200 if uploaded_files else 400

        return jsonify(response), status_code

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'message': 'Произошла ошибка при загрузке файлов',
            'error': str(e)
        }), 400


@api.route('/files/<int:file_id>/delete', methods=['POST'])
@token_required
def delete_file(file_id):
    try:
        # Пробуем найти файл сначала в TaskFile
        file = TaskFile.query.get(file_id)
        if file is None:
            # Если не нашли в TaskFile, ищем в CommentFile
            file = CommentFile.query.get(file_id)

        if file is None:
            return jsonify({
                'success': False,
                'message': 'Файл не найден'
            }), 404

        # Проверяем права на удаление
        if file.uploader_id != request.user['id']:
            return jsonify({
                'success': False,
                'message': 'Недостаточно прав для удаления файла'
            }), 403

        # Удаляем физический файл
        try:
            file_handler.delete_file(file.file_path)
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Ошибка при удалении файла из файловой системы: {str(e)}'
            }), 500

        # Удаляем запись из базы данных
        db.session.delete(file)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Файл успешно удален'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Произошла ошибка при удалении файла: {str(e)}'
        }), 400