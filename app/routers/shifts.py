from calendar import monthrange
from datetime import datetime

from flask import Blueprint, request, render_template, redirect, url_for
from app.db import db, Shift, User, Permission
from app.utils import token_required, permission_check

shifts = Blueprint('shifts', __name__, url_prefix='/shifts')


# Просмотр всех смен
@shifts.route('/', methods=['GET'])
@token_required
def get_all_shifts():
    user = request.user
    shifts = Shift.get_all()  # Получаем все смены
    permission_on_db = Permission.query.filter_by(page='shifts').all()
    permission = []
    for item in permission_on_db:
        perm_current = request.cookies.get(f'perm_{item.function}')
        permission.append({item.function: perm_current})

    today = datetime.now()
    current_day = today.day
    last_day_of_month = monthrange(today.year, today.month)[1]
    shift = []
    for vaxta in shifts:
        # Проверяем активность вахты
        if vaxta.start_day <= vaxta.end_day:  # Обычная вахта в пределах одного месяца
            vaxta.is_active = vaxta.start_day <= current_day <= vaxta.end_day
        else:  # Вахта, переходящая через границу месяца
            vaxta.is_active = current_day >= vaxta.start_day or current_day <= vaxta.end_day

            # Подсчитываем количество пользователей


        shift.append({
            'id': vaxta.id,
            'title': vaxta.title,
            'start_day': vaxta.start_day,
            'end_day': vaxta.end_day,
            'active': vaxta.is_active,
            'count': User.query.filter_by(shift_id=vaxta.id).count(),
            'itr': vaxta.itr,
        })

    db.session.commit()

    return render_template('shifts/all_shifts.html', shifts=shift, user=user, permission=permission)


@shifts.route('/update', methods=['POST'])
@token_required
def update_shift():
    form_data = request.form
    for key, value in form_data.items():
        if key.startswith('v') and key[1:].isdigit():
            shift_id = int(key[1:])  # Извлекаем ID из имени поля

            # Получаем объект вахты из базы данных
            vaxta = Shift.query.filter_by(id=shift_id).first()
            if vaxta:
                vaxta.title = value  # Обновляем название
                vaxta.start_day = int(form_data.get(f"startv{shift_id}", vaxta.start_day))
                vaxta.end_day = int(form_data.get(f"endv{shift_id}", vaxta.end_day))

        # Сохраняем все изменения
    db.session.commit()
    return redirect(url_for('shifts.get_all_shifts'))