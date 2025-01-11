from app.db import db
from datetime import datetime
from sqlalchemy import Index, Enum, event
import enum


class TaskStatus(enum.Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    ON_REVIEW = "on_review"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class TaskPriority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class ParticipantRole(enum.Enum):
    RESPONSIBLE = "responsible"  # Может выполнять и отмечать выполнение
    EXECUTOR = "executor"  # Может выполнять задачи
    OBSERVER = "observer"  # Может только наблюдать
    ADMIN = "admin"  # Полный доступ к задаче

class FileType(enum.Enum):
    DOCUMENT = "document"
    IMAGE = "image"
    VIDEO = "video"
    ARCHIVE = "archive"
    OTHER = "other"

class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    platform_id = db.Column(db.String(50), nullable=False, unique=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)

    # Основные поля
    priority = db.Column(db.Enum(TaskPriority), nullable=False)
    status = db.Column(db.Enum(TaskStatus), nullable=False, default=TaskStatus.NEW)
    deadline = db.Column(db.DateTime, nullable=True, index=True)

    # Создатель задачи
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Метаданные
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    completed_at = db.Column(db.DateTime, nullable=True)

    # Связи
    department_assignments = db.relationship('DepartmentTaskAssignment', backref='task', lazy='dynamic',
                                             cascade='all, delete-orphan')
    participants = db.relationship('TaskParticipant', backref='task', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('TaskComment', backref='task', lazy='dynamic', cascade='all, delete-orphan')
    checklists = db.relationship('TaskChecklist', backref='task', lazy='dynamic', cascade='all, delete-orphan')
    files = db.relationship('TaskFile', backref='task', lazy='dynamic', cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        super(Task, self).__init__(**kwargs)

    def __repr__(self):
        return f'<Task {self.title}>'

class DepartmentTaskAssignment(db.Model):
    """Назначение задачи на отдел с отслеживанием прогресса"""
    __tablename__ = 'department_task_assignments'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    status = db.Column(db.Enum(TaskStatus), nullable=False, default=TaskStatus.NEW)
    progress = db.Column(db.Integer, default=0)  # Процент выполнения
    deadline = db.Column(db.DateTime, nullable=True)  # Опциональный дедлайн для отдела

    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    __table_args__ = (
        Index('idx_task_dept', task_id, department_id, unique=True),
    )

class TaskParticipant(db.Model):
    """Участники задачи с ролями"""
    __tablename__ = 'task_participants'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    role = db.Column(db.Enum(ParticipantRole), nullable=False)

    joined_at = db.Column(db.DateTime, default=datetime.now)
    time_spent = db.Column(db.Integer, default=0)  # Время в минутах

    __table_args__ = (
        Index('idx_task_user_unique', task_id, user_id, unique=True),
    )

class TaskChecklist(db.Model):
    """Чек-лист задачи"""
    __tablename__ = 'task_checklists'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    items = db.relationship('ChecklistItem', backref='checklist', lazy='dynamic')

class ChecklistItem(db.Model):
    """Элемент чек-листа"""
    __tablename__ = 'checklist_items'

    id = db.Column(db.Integer, primary_key=True)
    checklist_id = db.Column(db.Integer, db.ForeignKey('task_checklists.id'), nullable=False)
    content = db.Column(db.String(255), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)

    is_completed = db.Column(db.Boolean, default=False)
    completed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.now)
    weight = db.Column(db.Integer, default=1)  # Вес для расчета прогресса

class TaskFile(db.Model):
    """Файлы, прикрепленные к задаче"""
    __tablename__ = 'task_files'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    uploader_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)

    # Информация о файле
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.Enum(FileType), nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)  # размер в байтах
    file_path = db.Column(db.String(512), nullable=False)

    # Метаданные
    uploaded_at = db.Column(db.DateTime, default=datetime.now)
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    deleted_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    def __init__(self, **kwargs):
        super(TaskFile, self).__init__(**kwargs)

    def __repr__(self):
        return f'<TaskFile {self.original_filename}>'

    def soft_delete(self, user_id):
        """Мягкое удаление файла"""
        self.is_deleted = True
        self.deleted_at = datetime.now()
        self.deleted_by = user_id
        db.session.commit()

class CommentFile(db.Model):
    """Файлы, прикрепленные к комментариям"""
    __tablename__ = 'comment_files'

    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('task_comments.id'), nullable=False)
    uploader_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Информация о файле
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.Enum(FileType), nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    file_path = db.Column(db.String(512), nullable=False)

    # Метаданные
    uploaded_at = db.Column(db.DateTime, default=datetime.now)
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    deleted_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    def __init__(self, **kwargs):
        super(CommentFile, self).__init__(**kwargs)

    def __repr__(self):
        return f'<CommentFile {self.original_filename}>'

    def soft_delete(self, user_id):
        """Мягкое удаление файла"""
        self.is_deleted = True
        self.deleted_at = datetime.now()
        self.deleted_by = user_id
        db.session.commit()

class TaskComment(db.Model):
    __tablename__ = 'task_comments'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    content = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # Добавляем связь с файлами
    files = db.relationship('CommentFile', backref='comment', lazy='dynamic', cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        super(TaskComment, self).__init__(**kwargs)

    def __repr__(self):
        return f'<TaskComment {self.id}>'


# Триггеры для автоматического обновления прогресса
@event.listens_for(ChecklistItem, 'after_update')
def update_department_progress(mapper, connection, target):
    """Обновляет прогресс отдела при изменении статуса чек-листа"""
    if target.department_id:
        # Здесь должна быть логика подсчета прогресса для отдела
        pass