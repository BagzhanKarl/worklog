from app.db import db
from datetime import datetime
from app.utils import hash_password, check_password


class User(db.Model):
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
    shift_id = db.Column(db.Integer, db.ForeignKey('shift.id'), nullable=True)

    start_day = db.Column(db.Integer, nullable=True)
    end_day = db.Column(db.Integer, nullable=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())


    def __init__(self, first_name, second_name, third_name, phone, job_title, department_id, shift_id, role_id, is_admin):
        self.first_name = first_name
        self.second_name = second_name
        self.third_name = third_name
        self.phone = phone
        self.job_title = job_title
        self.department_id = department_id
        self.shift_id = shift_id
        self.role_id = role_id
        self.is_admin = is_admin

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
        return self

    # Utility methods for model
    def set_password(self, password):
        """Set hashed password."""
        self.password = hash_password(password)

    def check_password(self, password):
        """Check hashed password."""
        return check_password(password, self.password)

    def activate_account(self):
        """Activate the users account."""
        self.is_active = True
        self.is_banned = False

    def deactivate_account(self):
        """Deactivate the users account."""
        self.is_active = False

    def ban_user(self):
        """Ban the users."""
        self.is_banned = True
        self.is_active = False

    def unban_user(self):
        """Unban the users."""
        self.is_banned = False
        self.is_active = True

    def delete_account(self):
        """Mark account as deleted."""
        self.is_deleted = True
        self.is_active = False

    @classmethod
    def get_by_id(cls, user_id):
        """Get users by ID."""
        return cls.query.filter_by(id=user_id).first()

    @classmethod
    def get_all(cls):
        """Get all users."""
        return cls.query.all()

    @classmethod
    def get_active_users(cls):
        """Get all active users."""
        return cls.query.filter_by(is_active=True, is_deleted=False).all()

    def __repr__(self):
        return f"<User {self.first_name} {self.second_name}>"

