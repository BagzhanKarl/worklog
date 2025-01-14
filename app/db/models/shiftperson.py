from datetime import datetime

from app.db import db

class ShiftPerson(db.Model):
    __tablename__ = 'shift_person'

    id = db.Column(db.Integer, primary_key=True)

    first_user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    second_user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __init__(self, first_user, second_user=None):
        self.first_user = first_user
        self.second_user = second_user

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_partner(cls, user_id):
        """
        Находит напарника для пользователя по его ID

        Args:
            user_id (int): ID пользователя, для которого ищем напарника

        Returns:
            int|None: ID напарника если найден, None если не найден
        """
        # Ищем где пользователь является первым участником
        shift = cls.query.filter_by(first_user=user_id).first()
        if shift:
            return shift.second_user

        # Ищем где пользователь является вторым участником
        shift = cls.query.filter_by(second_user=user_id).first()
        if shift:
            return shift.first_user

        return None


class ReportShift(db.Model):
    __tablename__ = 'report_shift'

    id = db.Column(db.Integer, primary_key=True)
    from_on = db.Column(db.DateTime, nullable=False)
    to = db.Column(db.DateTime, nullable=False)

    completed = db.Column(db.Text)
    needed = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    can_see = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)