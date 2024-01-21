from collections import namedtuple
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

icons_legacy = {
    "stylesheets": ["legacy-icons.css"],
    "alert": "glyphicon glyphicon-warning-sign",
    "arrowDown": "glyphicon glyphicon-arrow-down",
    "arrowUp": "glyphicon glyphicon-arrow-up",
    "btnArchive": {
        "common": "legacy-icon",
        "active": "legacy-icon-archived",
        "inactive": "legacy-icon-unarchived",
    },
    "btnCollaborate": {
        "common": "legacy-icon",
        "active": "legacy-icon-non-collaborative",
        "inactive": "legacy-icon-collaborative",
    },
    "btnShowParentActions": {
        "common": "glyphicon",
        "active": "glyphicon-eye-open",
        "inactive": "glyphicon-eye-close",
    },
    "changeImage": "legacy-icon legacy-icon-change-image",
    "childItem": "glyphicon glyphicon-level-up",
    "edit": "legacy-icon legacy-icon-edit",
    "file": "legacy-icon legacy-icon-file",
    "folder": "legacy-icon legacy-icon-folder",
    "folderInaccessible": "legacy-icon legacy-icon-folder-inaccessible",
    "help": "glyphicon glyphicon-question-sign",
    "highDef": "glyphicon glyphicon-hd-video",
    "highlightInTree": "glyphicon glyphicon-search",
    "home": "glyphicon glyphicon-home",
    "invisible": "glyphicon glyphicon-eye-close",
    "lock": "glyphicon glyphicon-lock",
    "loader": "legacy-icon legacy-icon-loader",
    "login": "glyphicon glyphicon-log-in",
    "logout": "glyphicon glyphicon-log-out",
    "markAsNews": "glyphicon glyphicon-flag",
    "navCaret": {
        "common": " glyphicon",
        "collapsed": "glyphicon-expand",
        "expanded": "glyphicon-collapse-down",
    },
    "networkDrive": "legacy-icon legacy-icon-network-drive",
    "newItem": "glyphicon glyphicon-plus",
    "ok": "glyphicon glyphicon-ok",
    "pencil": "fa-pencil",
    "printer": "glyphicon glyphicon-print",
    "remove": "glyphicon glyphicon-remove",
    "scrollToBottom": "glyphicon glyphicon-arrow-down",
    "selectSample": {
        "common": " glyphicon",
    },
    "settings": "glyphicon glyphicon-wrench",
    "shuffle": "glyphicon glyphicon-resize-vertical",
    "sortAlphabet": "glyphicon glyphicon-sort-by-alphabet",
    "sortCalendar": "glyphicon glyphicon-calendar",
    "sortNumber": "glyphicon glyphicon-sort-by-order",
    "toggleHeaderNav": "glyphicon glyphicon-option-vertical",
    "toggleTree": "glyphicon glyphicon-menu-hamburger",
    "sample": "legacy-icon legacy-icon-sample",
    "trash": "glyphicon glyphicon-trash",
    "trashAlt": "legacy-icon legacy-icon-trash",
    "upload": "legacy-icon legacy-icon-upload",
    "user": "glyphicon glyphicon-user",
    "userAlt": "legacy-icon legacy-icon-user",
    "visible": "glyphicon glyphicon-eye-open",
}

icons_dict = icons_legacy
icons = namedtuple("icons", icons_dict.keys())(**icons_dict)


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
        icons=icons,
        js_view=js_view,
        js_params=js_params,
        racine_version=RACINE_VERSION,
        **kwargs,
    )
