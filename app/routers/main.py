from flask import Blueprint, render_template, request

from app.utils import token_required

main = Blueprint('main', __name__)

@main.route('/')
@token_required
def index():
    user = request.user
    return render_template('main/index.html', user=user)