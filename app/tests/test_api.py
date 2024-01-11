import os
import pytest
from flask.testing import FlaskClient
from flask_migrate import upgrade  # , downgrade
from werkzeug.test import TestResponse

from .. import create_app


class Context:
    def __init__(self, app, client: FlaskClient, api_token: str):
        self.app = app
        self.client = client
        self.api_token = api_token


def expect_status_code(r: TestResponse, code: int):
    assert r.status_code == code, f"Expected status code {code}, got {r.status_code}, response: {r.data.decode('utf-8')}"


g_ctx = None


@pytest.fixture()
def ctx():
    global g_ctx
    if g_ctx is not None:
        yield g_ctx
        return

    app = create_app("testing")

    # make sure that testing DB does not exist
    db_path = app.config.get("SQLALCHEMY_DATABASE_URI").replace("sqlite:///", "")
    if os.path.exists(db_path):
        os.remove(db_path)

    with app.app_context():
        upgrade()

    # recreate app to initialize activity table
    app = create_app("testing")

    # get API token
    with app.test_client() as client:
        # log in via HTTP
        r = client.post("/auth/login", data={"username": "admin", "password": "admin"})
        assert r.status_code == 302

        r = client.get("/").data.decode("utf-8")
        i = r.index('R.init("') + 8
        j = r.index('",', i)
        api_token = r[i:j]

        g_ctx = Context(app, client, api_token)
        yield g_ctx
        return

    g_ctx = None
    raise Exception("Could not create app context")


def test_create_users(ctx: Context):
    """Test that users can be created using the API."""
    r = ctx.client.put(
        "/api/user",
        headers={"Authorization": "Bearer " + ctx.api_token},
        data={
            "username": "Alice",
            "email": "alice@test.com",
            "password": "test",
            "password2": "test",
            "is_admin": False,
        },
    )
    expect_status_code(r, 201)


def test_create_user_with_existing_username(ctx: Context):
    """Test that users cannot be created if username already exists."""
    r = ctx.client.put(
        "/api/user",
        headers={"Authorization": "Bearer " + ctx.api_token},
        data={
            "username": "Alice",
            "email": "alice2@test.com",
            "password": "test",
            "password2": "test",
            "is_admin": False,
        },
    )
    expect_status_code(r, 400)


def test_create_user_with_existing_email(ctx: Context):
    """Test that users cannot be created if email already exists."""
    r = ctx.client.put(
        "/api/user",
        headers={"Authorization": "Bearer " + ctx.api_token},
        data={
            "username": "Alice2",
            "email": "alice@test.com",
            "password": "test",
            "password2": "test",
            "is_admin": False,
        },
    )
    expect_status_code(r, 400)
