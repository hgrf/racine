import os
import traceback

from flask import current_app
from flask import Flask

from wtforms.fields import HiddenField

from .abstract.async_task import async_init_app
from .abstract.kv_store import kvs_init_app
from .api.fields import maybe_update_activity_types
from .common import db, login_manager, migrate, render_racine_template
from .config import config
from .usagestats import usage_stats_task

from .api import api as api_blueprint
from .main import main as main_blueprint
from .auth import auth as auth_blueprint
from .browser import browser as browser_blueprint
from .settings import settings as settings_blueprint
from .profile import profile as profile_blueprint
from .printdata import printdata as printdata_blueprint


def error_handler(e):
    if current_app.config["LOG_EXCEPTIONS"]:
        current_app.logger.error("Unhandled Exception: %s", traceback.format_exc())
        return render_racine_template("errors/500.html", use_api=False), 500
    else:
        raise


def create_app(config_name=os.getenv("FLASK_CONFIG") or "default"):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    maybe_update_activity_types(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    async_init_app(app)
    kvs_init_app(app)
    if not app.config["TESTING"]:
        usage_stats_task.delay()

    # https://github.com/mbr/flask-bootstrap/blob/3.3.7.1/flask_bootstrap/__init__.py
    app.jinja_env.globals["bootstrap_is_hidden_field"] = lambda field: isinstance(
        field, HiddenField
    )

    app.register_error_handler(Exception, error_handler)

    app.register_blueprint(api_blueprint, url_prefix="/api")
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint, url_prefix="/auth")
    app.register_blueprint(browser_blueprint, url_prefix="/browser")
    app.register_blueprint(settings_blueprint, url_prefix="/settings")
    app.register_blueprint(profile_blueprint, url_prefix="/profile")
    app.register_blueprint(printdata_blueprint, url_prefix="/print")

    return app
