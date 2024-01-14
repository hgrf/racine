from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user, LoginManager
from flask_migrate import Migrate

from .version import RACINE_VERSION

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "auth.login"
migrate = Migrate()


def render_racine_template(template: str, js_view="", js_params={}, use_api=True, **kwargs):
    """Render a template with the common parameters.

    :param template: the template to render
    :param js_view: the name of the javascript view to load
    :param js_params: the parameters to pass to the javascript view
    :param use_api: whether to pass the API token to the template (since the API can currently
                    only used by logged-in users, this has to be set to False on the auth pages)
    :param kwargs: additional parameters to pass to the template
    """
    return render_template(
        template,
        api_token=current_user.get_token() if use_api else "",
        js_view=js_view,
        js_params=js_params,
        racine_version=RACINE_VERSION,
        **kwargs,
    )
