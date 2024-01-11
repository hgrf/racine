import os
from flask_migrate import upgrade  # , downgrade

from .. import create_app


def test_create_users():
    """Test that users can be created using the API."""
    app = create_app("testing")

    # make sure that testing DB does not exist
    db_path = app.config.get("SQLALCHEMY_DATABASE_URI").replace("sqlite:///", "")
    if os.path.exists(db_path):
        os.remove(db_path)

    with app.app_context():
        upgrade()

    # recreate app to initialize activity table
    app = create_app("testing")

    with app.test_client() as c:
        # log in via HTTP
        r = c.post("/auth/login", data={"username": "admin", "password": "admin"})
        assert r.status_code == 302

        r = c.get("/").data.decode("utf-8")
        i = r.index("R.init(\"") + 8
        j = r.index("\",", i)
        api_token = r[i : j]

        r = c.put(
            "/api/user",
            headers={"Authorization": "Bearer " + api_token},
            data={
                "username": "testuser",
                "email": "test@test.com",
                "password": "test",
                "password2": "test",
                "is_admin": False,
            }
        )
        assert r.status_code == 201
