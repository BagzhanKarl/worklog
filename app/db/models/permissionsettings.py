from app.db import db
from datetime import datetime
from functools import wraps

# Модель для разрешений, назначенных для ролей
class RolePermission(db.Model):
    __tablename__ = 'role_permissions'

    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False, index=True)
    permission_id = db.Column(db.Integer, db.ForeignKey('permissions.id'), nullable=False, index=True)
    is_granted = db.Column(db.Boolean, nullable=False, default=True)  # Разрешено ли действие
    created_at = db.Column(db.DateTime, default=datetime.now, index=True)  # Когда было назначено разрешение



    def __init__(self, role_id, permission_id, is_granted=True):
        self.role_id = role_id
        self.permission_id = permission_id
        self.is_granted = is_granted

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_permissions_for_role(cls, role_id):
        return cls.query.filter_by(role_id=role_id).all()

    def __repr__(self):
        return f"<RolePermission (Role ID: {self.role_id}, Permission ID: {self.permission_id}, Granted: {self.is_granted})>"


# Модель для разрешений, назначенных пользователям
class UserPermission(db.Model):
    __tablename__ = 'user_permissions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    permission_id = db.Column(db.Integer, db.ForeignKey('permissions.id'), nullable=False, index=True)
    is_granted = db.Column(db.Boolean, nullable=False, default=True)  # Разрешено ли действие
    created_at = db.Column(db.DateTime, default=datetime.now, index=True)  # Когда было назначено разрешение



    def __init__(self, user_id, permission_id, is_granted=True):
        self.user_id = user_id
        self.permission_id = permission_id
        self.is_granted = is_granted

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return f"<UserPermission (User ID: {self.user_id}, Permission ID: {self.permission_id}, Granted: {self.is_granted})>"


# Модель для разрешений, назначенных для отделов
class DepartmentPermission(db.Model):
    __tablename__ = 'department_permissions'

    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False, index=True)
    permission_id = db.Column(db.Integer, db.ForeignKey('permissions.id'), nullable=False, index=True)
    is_granted = db.Column(db.Boolean, nullable=False, default=True)  # Разрешено ли действие
    created_at = db.Column(db.DateTime, default=datetime.now, index=True)  # Когда было назначено разрешение



    def __init__(self, department_id, permission_id, is_granted=True):
        self.department_id = department_id
        self.permission_id = permission_id
        self.is_granted = is_granted

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_permissions_for_department(cls, department_id):
        return cls.query.filter_by(department_id=department_id).all()

    def __repr__(self):
        return f"<DepartmentPermission (Department ID: {self.department_id}, Permission ID: {self.permission_id}, Granted: {self.is_granted})>"


