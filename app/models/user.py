import base64
import json
import os

from authlib.jose import JsonWebSignature
from datetime import datetime, timedelta
from flask import current_app as app
from flask_httpauth import HTTPTokenAuth
from flask_login import UserMixin
from flask_login import current_user as flask_login_current_user
from werkzeug.security import generate_password_hash, check_password_hash

from .. import db, login_manager

token_auth = HTTPTokenAuth()


@token_auth.verify_token
def verify_token(token):
    return User.check_token(token) if token else None


@token_auth.error_handler
def token_auth_error(status):
    return "", 500  # error_response(status)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def current_user():
    return token_auth.current_user() or flask_login_current_user


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)
    is_admin = db.Column(db.Boolean())
    samples = db.relationship("Sample", backref="owner")
    actions = db.relationship("Action", backref="owner")
    shares = db.relationship("Share", backref="user")
    uploads = db.relationship("Upload", backref="user")
    activity = db.relationship("Activity", backref="user")
    heir_id = db.Column(
        db.Integer, db.ForeignKey("users.id")
    )  # ID of the user who inherits this users data

    inheritance = db.relationship(
        "User", backref=db.backref("heir", remote_side=[id])
    )  # Users who gave their data to this one

    def __repr__(self):
        return "<User %r>" % self.username

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_reset_token(self, expiration=3600):
        jws = JsonWebSignature()
        return jws.serialize_compact(
            {"alg": "HS256"}, json.dumps({"reset": self.id}), app.config["SECRET_KEY"]
        )

    @staticmethod
    def reset_password(token, new_password):
        jws = JsonWebSignature()
        try:
            data = jws.deserialize_compact(token, app.config["SECRET_KEY"])
            data = json.loads(data["payload"])
        except Exception:
            return False
        user = User.query.get(data.get("reset"))
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        return True

    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode("utf-8")
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user
