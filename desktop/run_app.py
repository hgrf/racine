import os
import sys
import traceback

from logging.config import fileConfig  # noqa: F401
from flask_migrate import upgrade

# NOTE: workaround to make decorators for async tasks work correctly
os.environ["USE_THREADED_ASYNC"] = "1"

if __name__ == "__main__":
    try:
        print("Changing to working directory...")
        workdir = os.path.join(
            os.environ.get("HOME") or os.environ.get("USERPROFILE"), "RacineDesktop"
        )
        os.makedirs(workdir, exist_ok=True)
        os.chdir(workdir)
        print("Creating directories...")
        os.makedirs("data", exist_ok=True)
        os.makedirs("database", exist_ok=True)
        os.makedirs("uploads", exist_ok=True)

        print("Creating app...")

        from app import create_app

        app = create_app("standalone")

        print("Running migrations...")
        with app.app_context():
            if os.path.exists(os.path.join(os.path.dirname(__file__), "migrations")):
                # for dist
                upgrade(os.path.join(os.path.dirname(__file__), "migrations"))
            else:
                # for dev
                upgrade(os.path.join(os.path.dirname(__file__), "..", "migrations"))

        # recreate the app to make sure activity types are initialized
        app = create_app("standalone")

        print("Running app...")
        app.run(port=4040)
    except Exception as e:
        traceback.print_exception(e)
        sys.exit(1)
