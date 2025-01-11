from app.db import db
from datetime import datetime

class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    icon = db.Column(db.String(64), nullable=False)
    color = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())



    def __init__(self, id=None, name=None, description=None, icon=None, color=None):
        self.name = name
        self.description = description
        self.icon = icon
        self.color = color

    def save_to_db(self):
        """Save or update the department in the database."""
        db.session.add(self)
        db.session.commit()
        return True

    def update(self, name=None, description=None, icon=None, color=None):
        """Update department details."""
        if name:
            self.name = name
        if description:
            self.description = description
        if icon:
            self.icon = icon
        if color:
            self.color = color
        self.updated_at = datetime.now()
        db.session.commit()

    def delete(self):
        """Delete the department."""
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_by_id(cls, department_id):
        """Get department by ID."""
        return cls.query.filter_by(id=department_id).first()

    @classmethod
    def get_all(cls):
        """Get all departments."""
        return cls.query.all()

    @classmethod
    def get_active_departments(cls):
        """Get active departments (if there were an 'is_active' flag)."""
        return cls.query.filter_by(is_active=True).all()

    def __repr__(self):
        return f"<Department {self.name}>"

