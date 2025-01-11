from app.db import db
from datetime import datetime
from sqlalchemy import Index

class Report(db.Model):
    __tablename__ = 'reports'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False, index=True)
    report_content = db.Column(db.Text, nullable=False)
    created_by = db.Column(db.Integer, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.now, index=True)



    __table_args__ = (
        Index('ix_reports_task_id_created_by', 'task_id', 'created_by'),
    )

    def __init__(self, task_id, report_content, created_by):
        self.task_id = task_id
        self.report_content = report_content
        self.created_by = created_by

    def save_to_db(self):
        """Сохранить отчет в базе данных."""
        db.session.add(self)
        db.session.commit()

    def update_report(self, new_report_content):
        """Обновить содержание отчета."""
        self.report_content = new_report_content
        db.session.commit()

    def delete_report(self):
        """Удалить отчет из базы данных."""
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_by_task_id(cls, task_id):
        """Получить все отчеты по task_id."""
        return cls.query.filter_by(task_id=task_id).all()

    @classmethod
    def get_by_id(cls, report_id):
        """Получить отчет по его ID."""
        return cls.query.get(report_id)

    def __repr__(self):
        return f"<Report (Task ID: {self.task_id}, Created by: {self.created_by})>"
