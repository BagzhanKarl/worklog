from app.db import db
from datetime import datetime
from sqlalchemy import Index, event

# Модель задачи
class Tasks(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    task_platform_id = db.Column(db.String(50), nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    priority = db.Column(db.String(10), nullable=False)  # high, medium, low
    status = db.Column(db.String(10), nullable=False)  # new, inprocess, testing, done
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False, index=True)
    deadline = db.Column(db.DateTime, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.now, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    department = db.relationship('Department', backref=db.backref('tasks', lazy=True))

    __table_args__ = (
        Index('ix_tasks_task_platform_id_deadline', 'task_platform_id', 'deadline'),
    )

    def __init__(self, task_platform_id, title, description, priority, status, department_id, deadline):
        self.task_platform_id = task_platform_id
        self.title = title
        self.description = description
        self.priority = priority
        self.status = status
        self.department_id = department_id
        self.deadline = deadline

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def update_task(updated_task_data):
        task = Tasks.query.get(updated_task_data['id'])
        if task:
            task.title = updated_task_data.get('title', task.title)
            task.description = updated_task_data.get('description', task.description)
            task.priority = updated_task_data.get('priority', task.priority)
            task.status = updated_task_data.get('status', task.status)
            task.deadline = updated_task_data.get('deadline', task.deadline)
            task.updated_at = datetime.now()
            db.session.commit()


# Модель участников задачи
class TaskParticipant(db.Model):
    __tablename__ = 'task_participants'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)  # ID пользователя
    role = db.Column(db.String(50), nullable=True)  # Роль участника в задаче (e.g., "исполнитель", "наблюдатель")
    created_at = db.Column(db.DateTime, default=datetime.now, index=True)

    task = db.relationship('Tasks', backref=db.backref('participants', lazy=True))

    __table_args__ = (
        Index('ix_task_participants_task_id_user_id', 'task_id', 'user_id'),
    )

    def __init__(self, task_id, user_id, role=None):
        self.task_id = task_id
        self.user_id = user_id
        self.role = role

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def add_participant(task_id, user_id, role=None):
        participant = TaskParticipant(task_id=task_id, user_id=user_id, role=role)
        db.session.add(participant)
        db.session.commit()

    @staticmethod
    def remove_participant(task_id, user_id):
        participant = TaskParticipant.query.filter_by(task_id=task_id, user_id=user_id).first()
        if participant:
            db.session.delete(participant)
            db.session.commit()

    @staticmethod
    def get_participants(task_id):
        return TaskParticipant.query.filter_by(task_id=task_id).all()


# Модель чеклиста
class Checklist(db.Model):
    __tablename__ = 'checklists'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False, index=True)
    item = db.Column(db.String(255), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now, index=True)

    task = db.relationship('Tasks', backref=db.backref('checklists', lazy=True))

    __table_args__ = (
        Index('ix_checklist_task_id_created_at', 'task_id', 'created_at'),
    )

    def __init__(self, task_id, item, is_completed=False):
        self.task_id = task_id
        self.item = item
        self.is_completed = is_completed

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()


# Модель комментариев
class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, index=True)

    task = db.relationship('Tasks', backref=db.backref('comments', lazy=True))

    __table_args__ = (
        Index('ix_comments_task_id_user_id_created_at', 'task_id', 'user_id', 'created_at'),
    )

    def __init__(self, task_id, user_id, text):
        self.task_id = task_id
        self.user_id = user_id
        self.text = text

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()


# Модель файлов
class File(db.Model):
    __tablename__ = 'files'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False, index=True)
    file_url = db.Column(db.String(255), nullable=False)
    original_file_name = db.Column(db.String(255), nullable=False)
    uploaded_by = db.Column(db.Integer, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.now, index=True)

    task = db.relationship('Tasks', backref=db.backref('files', lazy=True))

    __table_args__ = (
        Index('ix_files_task_id_uploaded_by', 'task_id', 'uploaded_by'),
    )

    def __init__(self, task_id, file_url, uploaded_by, original_file_name):
        self.task_id = task_id
        self.file_url = file_url
        self.uploaded_by = uploaded_by
        self.original_file_name = original_file_name

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()


# Модель отчёта
class Report(db.Model):
    __tablename__ = 'reports'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False, index=True)
    report_content = db.Column(db.Text, nullable=False)
    created_by = db.Column(db.Integer, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.now, index=True)

    task = db.relationship('Tasks', backref=db.backref('reports', lazy=True))

    __table_args__ = (
        Index('ix_reports_task_id_created_by', 'task_id', 'created_by'),
    )

    def __init__(self, task_id, report_content, created_by):
        self.task_id = task_id
        self.report_content = report_content
        self.created_by = created_by

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()


# Обработчики событий для обновления задачи
@event.listens_for(Checklist, 'after_insert')
@event.listens_for(Checklist, 'after_update')
@event.listens_for(Checklist, 'after_delete')
def update_task_on_checklist_change(mapper, connection, target):
    task = Tasks.query.get(target.task_id)
    if task:
        task.updated_at = datetime.now()  # обновляем время обновления задачи
        db.session.commit()

@event.listens_for(Comment, 'after_insert')
@event.listens_for(Comment, 'after_update')
@event.listens_for(Comment, 'after_delete')
def update_task_on_comment_change(mapper, connection, target):
    task = Tasks.query.get(target.task_id)
    if task:
        task.updated_at = datetime.now()  # обновляем время обновления задачи
        db.session.commit()

@event.listens_for(File, 'after_insert')
@event.listens_for(File, 'after_update')
@event.listens_for(File, 'after_delete')
def update_task_on_file_change(mapper, connection, target):
    task = Tasks.query.get(target.task_id)
    if task:
        task.updated_at = datetime.now()  # обновляем время обновления задачи
        db.session.commit()

@event.listens_for(Report, 'after_insert')
@event.listens_for(Report, 'after_update')
@event.listens_for(Report, 'after_delete')
def update_task_on_report_change(mapper, connection, target):
    task = Tasks.query.get(target.task_id)
    if task:
        task.updated_at = datetime.now()  # обновляем время обновления задачи
        db.session.commit()

# Обработчик событий для обновления задачи при изменении участников
@event.listens_for(TaskParticipant, 'after_insert')
@event.listens_for(TaskParticipant, 'after_delete')
def update_task_on_participant_change(mapper, connection, target):
    task = Tasks.query.get(target.task_id)
    if task:
        task.updated_at = datetime.now()  # обновляем время обновления задачи
        db.session.commit()
