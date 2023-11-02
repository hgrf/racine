import imp
import os
import subprocess

from celery import Celery, Task
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from glob import glob

from wtforms.fields import HiddenField

from .config import config


def is_hidden_field_filter(field):
    return isinstance(field, HiddenField)


with open(os.path.join(os.path.dirname(__file__), "..", "version.csv"), "r") as f:
    RACINE_VERSION = None
    RACINE_API_VERSION = None
    for line in f:
        key, val = line.split(",", 1)
        if key == "RACINE_VERSION":
            RACINE_VERSION = val.strip()
        elif key == "RACINE_API_VERSION":
            RACINE_API_VERSION = val.strip()

    if RACINE_VERSION is None or RACINE_API_VERSION is None:
        raise Exception("version.csv is missing RACINE_VERSION or RACINE_API_VERSION")


SQLALCHEMY_TRACK_MODIFICATIONS = False
plugins = []

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "auth.login"
migrate = Migrate()

# has to be here, because it will import db and login_manager from this file
from .smbinterface import SMBInterface  # noqa: E402

smbinterface = SMBInterface()

# has to be here, because it will import db from this file
from .usagestats import periodic_task  # noqa: F401, E261


def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.conf.update(
        dict(
            CELERYBEAT_SCHEDULE=dict(
                usage_stats_task=dict(
                    task="usage_stats_task",
                    schedule=60.0,
                )
            )
        )
    )
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app


def create_app(config_name=os.getenv("FLASK_CONFIG") or "default"):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    celery_init_app(app)

    # https://github.com/mbr/flask-bootstrap/blob/3.3.7.1/flask_bootstrap/__init__.py
    app.jinja_env.globals["bootstrap_is_hidden_field"] = is_hidden_field_filter

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
        from .api.fields import supported_targets
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
        except OperationalError:
            # in case the table is not created yet, do nothing (this happens
            # when we do 'flask db upgrade')
            pass

    # look for plugins
    plugin_files = glob("plugins/*/*.py")
    for f in plugin_files:
        p = imp.load_source(f[8:-3], f)
        if not hasattr(p, "display") or not hasattr(p, "title"):
            # TODO: report this some other way, e.g. raise Exception or log warning...
            print("Incompatible plugin: ", f[8:-3])
        plugins.append(p)

    return app
