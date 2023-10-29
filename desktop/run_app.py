import os
import sys

from celery import fixups  # noqa: F401
from celery.fixups import django  # noqa: F401
from logging.config import fileConfig  # noqa: F401
from flask_migrate import upgrade

if __name__ == "__main__":
    try:
        print("Creating directories...")
        os.makedirs("data", exist_ok=True)
        os.makedirs("database", exist_ok=True)
        os.makedirs("uploads", exist_ok=True)

        print("Creating app...")
        from app import create_app

        app = create_app("standalone")

        print("Running migrations...")
        with app.app_context():
            upgrade(os.path.join(os.path.dirname(__file__), "migrations"))

        print("Running app...")
        app.run(port=4040)
    except Exception as e:
        print(e)
        sys.exit(1)
