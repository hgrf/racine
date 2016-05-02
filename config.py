import os
import logging.handlers
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BOOTSTRAP_SERVE_LOCAL = True        # don't use CDN for Bootstrap resources (so app will work without Internet access)
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')

    @staticmethod
    def init_app(app):
        logging.basicConfig(format='%(asctime)-15s %(message)s')
        file_handler = logging.handlers.RotatingFileHandler(os.path.join(basedir, 'msm.log'), maxBytes=10000)
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'database/data-dev.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'database/data.sqlite')


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
