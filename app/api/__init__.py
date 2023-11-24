from flask import Blueprint

api = Blueprint("api", __name__)

from app.api import actions, emailing, errors, fields, samples, shares  # noqa: E402, F401
