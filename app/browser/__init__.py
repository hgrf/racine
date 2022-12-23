from flask import Blueprint

browser = Blueprint("browser", __name__)

from . import views  # noqa: E402,F401
