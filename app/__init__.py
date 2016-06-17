from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from config import config
from glob import glob
import imp

bootstrap = Bootstrap()
db = SQLAlchemy()

plugins = []

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

    # look for plugins
    plugin_files = glob('plugins/*.py')
    print "Plugins found: ", plugin_files
    for f in plugin_files:
        p = imp.load_source(f[8:-3], f)
        if not hasattr(p, 'display') or not hasattr(p, 'title'):
            print "Uncompatible plugin: ", f[8:-3]
        plugins.append(p)

    return app
