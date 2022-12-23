from flask import Blueprint

printdata = Blueprint("printdata", __name__)

from . import views  # noqa: E402,F401
