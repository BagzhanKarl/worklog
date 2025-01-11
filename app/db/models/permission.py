from app.db import db
from datetime import datetime


class Permission(db.Model):
    __tablename__ = 'permissions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    function = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    page = db.Column(db.String(50), nullable=False)  # Страница, к которой относится разрешение
    method = db.Column(db.Integer, nullable=False)  # Страница, к которой относится разрешение
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())

    def __init__(self, name=None, function=None, description=None, page=None, method=None):
        self.name = name
        self.function = function
        self.description = description
        self.page = page
        self.method = method

    def save_to_db(self):
        """Сохранить разрешение в базе данных."""
        db.session.add(self)
        db.session.commit()
        return True

    def update(self, name=None, function=None, description=None, page=None):
        """Обновить разрешение."""
        if name:
            self.name = name
        if function:
            self.function = function
        if description:
            self.description = description
        if page:
            self.page = page
        self.updated_at = datetime.now()
        db.session.commit()

    @classmethod
    def get_by_page(cls, page):
        """Получить все разрешения для конкретной страницы."""
        return cls.query.filter_by(page=page).all()

    @classmethod
    def get_grouped_permissions(cls):
        """Получить все разрешения, сгруппированные по страницам."""
        permissions = cls.query.all()
        grouped = {}
        for permission in permissions:
            if permission.page not in grouped:
                grouped[permission.page] = []
            grouped[permission.page].append(permission)
        return grouped

    # Остальные методы остаются без изменений
    def delete(self):
        """Удалить разрешение."""
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_by_id(cls, permission_id):
        """Получить разрешение по ID."""
        return cls.query.filter_by(id=permission_id).first()

    @classmethod
    def get_all(cls):
        """Получить все разрешения."""
        return cls.query.all()

    @classmethod
    def get_by_name(cls, name):
        """Получить разрешение по имени."""
        return cls.query.filter_by(name=name).first()

    def __repr__(self):
        return f"<Permission {self.name} ({self.page})>"