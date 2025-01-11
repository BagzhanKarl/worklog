from datetime import datetime
from app.db import db

class Shift(db.Model):
    __tablename__ = 'shift'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    start_day = db.Column(db.Integer, nullable=False)
    end_day = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False)
    itr = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())



    def __init__(self, title=None, start_day=None, end_day=None, is_active=True, id=None, itr=False):
        self.title = title
        self.start_day = start_day
        self.end_day = end_day
        self.is_active = is_active
        self.itr = itr

    def save_to_db(self):
        """Save or update the shift in the database."""
        db.session.add(self)
        db.session.commit()
        return True

    def update(self, title=None, start_day=None, end_day=None, is_active=None, itr=None):
        """Update shift details."""
        if title:
            self.title = title
        if start_day is not None:
            self.start_day = start_day
        if end_day is not None:
            self.end_day = end_day
        if is_active is not None:
            self.is_active = is_active
        if itr is not None:
            self.itr = itr
        self.updated_at = datetime.now()
        db.session.commit()

    def delete(self):
        """Delete the shift."""
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_by_id(cls, shift_id):
        """Get shift by ID."""
        return cls.query.filter_by(id=shift_id).first()

    @classmethod
    def get_all(cls):
        """Get all shifts."""
        return cls.query.all()

    @classmethod
    def get_active_shifts(cls):
        """Get active shifts."""
        return cls.query.filter_by(is_active=True).all()

    @classmethod
    def get_inactive_shifts(cls):
        """Get inactive shifts."""
        return cls.query.filter_by(is_active=False).all()

    def __repr__(self):
        return f"<Shift {self.title}>"
