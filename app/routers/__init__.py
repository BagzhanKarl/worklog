from app.routers.auth import auth_bp
from .install import install
from app.routers.admin import admin
from app.routers.main import main
from app.routers.shifts import shifts
from app.routers.departments import departments
from app.routers.users import users
from app.routers.tasks import tasks
from .taskapi import api

def register_routers(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(install)
    app.register_blueprint(api)
    app.register_blueprint(admin)
    app.register_blueprint(main)
    app.register_blueprint(shifts)
    app.register_blueprint(departments)
    app.register_blueprint(users)
    app.register_blueprint(tasks)

