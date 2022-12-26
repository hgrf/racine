import os

from .. import create_app, db
from flask_migrate import Migrate, upgrade  # , downgrade


def test_instantiate_app():
    """Test that the app can be instantiated."""
    app = create_app("testing")
    assert app is not None


def test_db_migrations():
    """Test that the database migrations can be run."""
    app = create_app("testing")
    migrate = Migrate()

    # make sure that testing DB does not exist
    db_path = app.config.get("SQLALCHEMY_DATABASE_URI").replace("sqlite:///", "")
    if os.path.exists(db_path):
        os.remove(db_path)

    with app.app_context():
        db.init_app(app)
        migrate.init_app(app, db)
        upgrade()
        # TODO: downgrading is not correctly implemented so far
        # downgrade(revision="base")
