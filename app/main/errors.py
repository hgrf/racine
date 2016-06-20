from flask import render_template
from . import main
from flask import current_app as app

@main.app_errorhandler(403)
def page_not_found(e):
    return render_template('403.html'), 403


@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@main.errorhandler(Exception)
def unhandled_exception(e):
    if app.config['LOG_EXCEPTIONS']:
        app.logger.error('Unhandled Exception: %s', (e))
        return render_template('500.html'), 500
    else:
        raise