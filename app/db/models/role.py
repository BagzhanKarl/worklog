from datetime import datetime
from app.db import db

class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)  # head, manager, users
    description = db.Column(db.String(255), nullable=True)  # описание роли, если нужно
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())



    def __init__(self, name=None, description=None):
        self.name = name
        self.description = description

    def save_to_db(self):
        """Сохранить или обновить роль в базе данных."""
        db.session.add(self)
        db.session.commit()
        return True

    def update(self, name=None, description=None):
        """Обновить данные роли."""
        if name:
            self.name = name
        if description:
            self.description = description
        self.updated_at = datetime.now()
        db.session.commit()

    def delete(self):
        """Удалить роль."""
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_by_id(cls, role_id):
        """Получить роль по ID."""
        return cls.query.filter_by(id=role_id).first()

    @classmethod
    def get_all(cls):
        """Получить все роли."""
        return cls.query.all()

    @classmethod
    def get_by_name(cls, name):
        """Получить роль по имени."""
        return cls.query.filter_by(name=name).first()

    def __repr__(self):
        return f"<Role {self.name}>"
