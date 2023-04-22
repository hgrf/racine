from flask import Blueprint

from .ajaxviews import ajaxviews as ajaxviews_blueprint

main = Blueprint("main", __name__)
main.register_blueprint(ajaxviews_blueprint, url_prefix="/aview")

from . import views, errors  # noqa: E402,F401
