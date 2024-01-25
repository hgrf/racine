from . import main
from ..common import render_racine_template


@main.app_errorhandler(403)
def forbidden(e):
    return render_racine_template("errors/403.html", use_api=False), 403


@main.app_errorhandler(404)
def page_not_found(e):
    return render_racine_template("errors/404.html", use_api=False), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    return render_racine_template("errors/500.html", use_api=False), 500
