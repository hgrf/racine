from flask import Blueprint

ajaxviews = Blueprint("ajaxviews", __name__)

from . import sample, search, tree, welcome  # noqa: E402,F401
