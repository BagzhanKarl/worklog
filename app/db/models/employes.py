from datetime import datetime
from app.db import db

class Vaxta(db.Model):
    __tablename__ = 'vaxta'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    start_day = db.Column(db.Integer, nullable=False)
    end_day = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False)
    iter = db.Column(db.Boolean, nullable=False)

    def __init__(self, title=None, start_day=None, end_day=None, is_active=None, id=None, iter=False):
        self.title = title
        self.start_day = start_day
        self.end_day = end_day
        self.is_active = is_active
        self.iter = iter

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
        return True

class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True) #head, manager, user

    def __init__(self, name=None):
        self.name = name

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
        return True

class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    icon = db.Column(db.String(64), nullable=False)
    color = db.Column(db.String(64), nullable=False)

    def __init__(self, id=None, name=None, description=None, icon=None, color=None):
        self.name = name
        self.description = description
        self.icon = icon
        self.color = color

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
        return True


class Employee(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    second_name = db.Column(db.String(80), nullable=False)
    third_name = db.Column(db.String(80), nullable=True)
    phone = db.Column(db.String(20), nullable=True, index=True)
    job_title = db.Column(db.String(80), nullable=True)
    password = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)
    is_banned = db.Column(db.Boolean, nullable=False, default=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    vaxta_id = db.Column(db.Integer, db.ForeignKey('vaxta.id'), nullable=True)

    start_day = db.Column(db.Integer, nullable=True)
    end_day = db.Column(db.Integer, nullable=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())

    def __init__(self, id=None, first_name=None, second_name=None, third_name=None, phone=None, password=None, job_title=None, role_id=None, department_id=None, vaxta_id=None):
        self.id = id
        self.first_name = first_name
        self.second_name = second_name
        self.third_name = third_name
        self.phone = phone
        self.job_title = job_title
        self.password = password
        self.role_id = role_id
        self.department_id = department_id
        self.vaxta_id = vaxta_id
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
        return True

    def get_user_by_phone(self):
        return self.query.filter_by(phone=self.phone).first()