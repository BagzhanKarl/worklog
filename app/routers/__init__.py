from app.routers.main import main
from app.routers.start import start_bp
from app.routers.auth import auth_bp
from app.routers.api import api

def register_routers(app):
    app.register_blueprint(main)
    app.register_blueprint(start_bp, url_prefix="/start")
    app.register_blueprint(auth_bp)
    app.register_blueprint(api)
