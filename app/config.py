import json
import os
import logging.handlers
from collections import namedtuple
from logging import Formatter

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class Config:
    STANDALONE = False
    SECRET_KEY = os.environ.get("SECRET_KEY") or "hard to guess string"
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BOOTSTRAP_SERVE_LOCAL = (
        True  # don't use CDN for Bootstrap resources (so app will work without Internet access)
    )
    RACINE_FOLDER = basedir
    UPLOAD_FOLDER = os.path.join(basedir, "uploads")
    CELERY = dict(
        broker_url="redis://racine-redis",
        result_backend="redis://racine-redis",
        task_ignore_result=True,
    )
    # can be one of "bootstrap", "legacy"
    ICON_THEME = "bootstrap"

    @staticmethod
    def init_app(app):
        file_handler = logging.handlers.RotatingFileHandler(
            os.path.join("data", "racine.log"), maxBytes=10000
        )
        file_handler.setFormatter(
            Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
        )
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)

        with open("app/static/icons/{}.json".format(app.config["ICON_THEME"]), "r") as f:
            icons_dict = json.load(f)
        app.config["ICONS"] = namedtuple("icons", icons_dict.keys())(**icons_dict)


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE_URL") or "sqlite:///" + os.path.join(
        basedir, "database/data-dev.sqlite"
    )
    LOG_EXCEPTIONS = (
        False  # do not catch and log exceptions (Flask development server provides info in browser)
    )


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///" + os.path.join(
        basedir, "database/data.sqlite"
    )
    LOG_EXCEPTIONS = True


class TestingConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///" + os.path.join(
        basedir, "database/testing.sqlite"
    )
    LOG_EXCEPTIONS = True
    TESTING = True
    WTF_CSRF_ENABLED = False
    CELERY = dict(
        task_always_eager=True,
    )


class StandaloneConfig(Config):
    STANDALONE = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///{}".format(
        os.path.join(os.getcwd(), "database", "data-sa.sqlite")
    )
    UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
    LOG_EXCEPTIONS = True
    CELERY = dict(
        task_always_eager=True,
    )


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "standalone": StandaloneConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
