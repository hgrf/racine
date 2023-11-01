import os
import sys
import traceback

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

        os.environ["RACINE_VERSION"] = "v0.1.0"
        os.environ["RACINE_API_VERSION"] = "0.1.0"

        from app import create_app

        app = create_app("standalone")

        print("Running migrations...")
        with app.app_context():
            upgrade(os.path.join(os.path.dirname(__file__), "migrations"))

        # recreate the app to make sure activity types are initialized
        app = create_app("standalone")

        print("Running app...")
        app.run(port=4040)
    except Exception as e:
        traceback.print_exception(e)
        sys.exit(1)
