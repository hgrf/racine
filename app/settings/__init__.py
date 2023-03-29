from flask import Blueprint

settings = Blueprint("settings", __name__)

from . import views  # noqa: E402,F401
