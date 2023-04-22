from flask import Blueprint

main = Blueprint("main", __name__)

from . import views, errors  # noqa: E402,F401
from .ajaxviews import tree, sample, welcome  # noqa: E402,F401
