import os
import logging.handlers
from logging import Formatter

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "hard to guess string"
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BOOTSTRAP_SERVE_LOCAL = (
        True  # don't use CDN for Bootstrap resources (so app will work without Internet access)
    )
    MSM_FOLDER = basedir
    UPLOAD_FOLDER = os.path.join(basedir, "uploads")

    @staticmethod
    def init_app(app):
        file_handler = logging.handlers.RotatingFileHandler(
            os.path.join(basedir, "msm.log"), maxBytes=10000
        )
        file_handler.setFormatter(
            Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
        )
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)


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


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
