from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .config import config
from glob import glob
import imp

SQLALCHEMY_TRACK_MODIFICATIONS = False
plugins = []

bootstrap = Bootstrap()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "auth.login"

from .smbinterface import (
    SMBInterface,
)  # has to be here, because it will import db and login_manager from this file

smbinterface = SMBInterface()
from .usagestats import (
    UsageStatisticsThread,
)  # has to be here, because it will import db from this file


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    from .api import api as api_blueprint
    from .main import main as main_blueprint
    from .auth import auth as auth_blueprint
    from .browser import browser as browser_blueprint
    from .settings import settings as settings_blueprint
    from .profile import profile as profile_blueprint
    from .printdata import printdata as printdata_blueprint

    app.register_blueprint(api_blueprint, url_prefix="/api")
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint, url_prefix="/auth")
    app.register_blueprint(browser_blueprint, url_prefix="/browser")
    app.register_blueprint(settings_blueprint, url_prefix="/settings")
    app.register_blueprint(profile_blueprint, url_prefix="/profile")
    app.register_blueprint(printdata_blueprint, url_prefix="/print")

    # update activity types table
    with app.app_context():
        from .main.views import supported_targets
        from .models import ActivityType
        from sqlalchemy.exc import OperationalError

        activity_types = ["selectsmbfile", "login", "logout"]
        try:
            registered_activity_types = [at.description for at in ActivityType.query.all()]

            for key, target in supported_targets.items():
                activity_types.append("add:" + key)
                activity_types.append("delete:" + key)
                for field in target["fields"]:
                    activity_types.append("update:" + key + ":" + field)

            for at in activity_types:
                if at not in registered_activity_types:
                    newat = ActivityType(description=at)
                    db.session.add(newat)
                    db.session.commit()
        except OperationalError as e:
            # in case the table is not created yet, do nothing (this happens when we do 'python manage.py db upgrade')
            pass

    # run usage statistics thread
    UsageStatisticsThread(app)

    # look for plugins
    plugin_files = glob("plugins/*/*.py")
    for f in plugin_files:
        p = imp.load_source(f[8:-3], f)
        if not hasattr(p, "display") or not hasattr(p, "title"):
            # TODO: report this some other way, e.g. raise Exception or log warning...
            print("Incompatible plugin: ", f[8:-3])
        plugins.append(p)

    return app
