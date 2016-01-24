from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from config import config

bootstrap = Bootstrap()
db = SQLAlchemy()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

SQLALCHEMY_TRACK_MODIFICATIONS = False

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    from .main import main as main_blueprint
    from .auth import auth as auth_blueprint
    from .browser import browser as browser_blueprint
    from .settings import settings as settings_blueprint
    from .profile import profile as profile_blueprint
    from .printdata import printdata as printdata_blueprint
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(browser_blueprint, url_prefix='/browser')
    app.register_blueprint(settings_blueprint, url_prefix='/settings')
    app.register_blueprint(profile_blueprint, url_prefix='/profile')
    app.register_blueprint(printdata_blueprint, url_prefix='/print')

    return app
