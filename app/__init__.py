
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_socketio import SocketIO
from config import Config


db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
socketio = SocketIO()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app, cors_allowed_origins="*")

    socketio.init_app(app)
    from app.events import game_events

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.game import bp as game_bp
    app.register_blueprint(game_bp)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    return app
    

from app import models
