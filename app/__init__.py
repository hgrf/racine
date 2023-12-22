import os

from celery import Celery, Task
from flask import Flask

from wtforms.fields import HiddenField

from .api.fields import maybe_update_activity_types
from .common import db, login_manager, migrate
from .config import config
from .smbinterface import SMBInterface

from .api import api as api_blueprint
from .main import main as main_blueprint
from .auth import auth as auth_blueprint
from .browser import browser as browser_blueprint
from .settings import settings as settings_blueprint
from .profile import profile as profile_blueprint
from .printdata import printdata as printdata_blueprint

smbinterface = SMBInterface()

SQLALCHEMY_TRACK_MODIFICATIONS = False


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
    maybe_update_activity_types(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    celery_init_app(app)

    # https://github.com/mbr/flask-bootstrap/blob/3.3.7.1/flask_bootstrap/__init__.py
    app.jinja_env.globals["bootstrap_is_hidden_field"] = lambda field: isinstance(
        field, HiddenField
    )

    app.register_blueprint(api_blueprint, url_prefix="/api")
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint, url_prefix="/auth")
    app.register_blueprint(browser_blueprint, url_prefix="/browser")
    app.register_blueprint(settings_blueprint, url_prefix="/settings")
    app.register_blueprint(profile_blueprint, url_prefix="/profile")
    app.register_blueprint(printdata_blueprint, url_prefix="/print")

    return app
