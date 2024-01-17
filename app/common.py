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

icons_bootstrap = {
    "stylesheets": [
        "bootstrap-icons.css",
    ],
    "extraStyles": {
        "editor.css": """
            div#sampledescription.editable-empty::before {
                content: '\\f4c9';
                font-family: 'bootstrap-icons';
            }
            i.editor-shortcut {
                font-size: 24px;
            }
        """,
        "navbar.css": """
            .navbar-shortcuts {
                font-size: 18px;
            }
        """,
    },
    "alert": "bi-exclamation-triangle-fill",
    "arrowDown": "bi-arrow-down-circle-fill",
    "arrowUp": "bi-arrow-up-circle-fill",
    "btnArchive": {
        "common": "",
        "active": "bi-archive-fill",
        "inactive": "bi-archive",
    },
    "btnCollaborate": {
        "common": "",
        "active": "bi-people-fill",
        "inactive": "bi-people-fill",
        "activeSub": "bi-pencil-fill",
        "inactiveSub": "bi-lock-fill",
    },
    "btnShowParentActions": {
        "common": "",
        "active": "bi-eye-fill",
        "inactive": "bi-eye-slash-fill",
    },
    "camera": "bi-camera-fill",
    "childItem": "bi-folder-symlink-fill",
    "edit": "bi-pencil-fill",
    "help": "bi-question-circle-fill",
    "highDef": "bi-badge-hd-fill",
    "highlightInTree": "bi-binoculars-fill",
    "home": "bi-house-fill",
    "invisible": "bi-eye-slash-fill",
    "lock": "bi-lock-fill",
    "login": "bi-box-arrow-in-right",
    "logout": "bi-door-closed-fill",
    "markAsNews": "bi-flag-fill",
    "navCaret": {
        "common": "",
        "collapsed": "bi-caret-right-fill",
        "expanded": "bi-caret-down-fill",
    },
    "networkDrive": "bi-hdd-network-fill",
    "newItem": "bi-plus-circle-fill",
    "ok": "bi-check-lg",
    "pencil": "bi-pencil-fill",
    "printer": "bi-printer-fill",
    "remove": "bi-x-square-fill",
    "scrollToBottom": "bi-file-earmark-arrow-down-fill",
    "selectSample": {
        "common": "",
    },
    "settings": "bi-gear-fill",
    "shuffle": "bi-shuffle",
    "sortAlphabet": "bi-sort-alpha-down",
    "sortCalendar": "bi-calendar-date-fill",
    "sortNumber": "bi-sort-numeric-down",
    "toggleHeaderNav": "bi-three-dots-vertical",
    "toggleTree": "bi-collection",
    "trash": "bi-trash3-fill",
    "upload": "bi-cloud-arrow-up-fill",
    "user": "bi-person-fill",
    "visible": "bi-eye-fill",
}

icons_fontawesome = {
    "stylesheets": [
        "fontawesome.min.css",
        "regular.min.css",
        "solid.min.css",
        "brands.min.css",
    ],
    "extraStyles": {
        "editor.css": """
            div#sampledescription.editable-empty::before {
                content: '\\f303';
                font-family: 'Font Awesome 6 Free';
                font-weight: 900;
            }
            i.editor-shortcut {
                font-size: 20px;
            }
        """,
        "navbar.css": """
            .navbar-shortcuts {
                font-size: 16px;
            }
            .navbar-shortcut.sort-active {
                padding: 2px;
            }
        """,
    },
    "alert": "fa-triangle-exclamation",
    "arrowDown": "fa-solid fa-circle-up",
    "arrowUp": "fa-solid fa-circle-down",
    "btnArchive": {
        "common": "fa-solid",
        "active": "fa-box-archive",
        "inactive": "fa-box-open",
    },
    "btnCollaborate": {
        "common": "fa-solid",
        "active": "fa-users",
        "inactive": "fa-users",
        "activeSub": "fa-pencil",
        "inactiveSub": "fa-lock",
    },
    "btnShowParentActions": {
        "common": " fa-solid",
        "active": "fa-eye",
        "inactive": "fa-eye-slash",
    },
    "camera": "fa-solid fa-camera",
    "childItem": "fa-solid fa-folder-tree",
    "edit": "fa-solid fa-pen-to-square",
    "help": "fa-solid fa-circle-question",
    "highDef": "fa-solid fa-photo-film",
    "highlightInTree": "fa-solid fa-glasses",
    "home": "fa-solid fa-house",
    "invisible": "fa-eye-slash",
    "lock": "fa-solid fa-lock",
    "login": "fa-solid fa-right-to-bracket",
    "logout": "fa-solid fa-door-closed",
    "markAsNews": "fa-solid fa-paper-plane",
    "navCaret": {
        "common": " fa-solid",
        "collapsed": "fa-caret-right",
        "expanded": "fa-caret-down",
    },
    "networkDrive": "fa-solid fa-server",
    "newItem": "fa-solid fa-circle-plus",
    "ok": "fa-check",
    "pencil": "fa-pencil",
    "printer": "fa-solid fa-print",
    "remove": "fa-solid fa-square-xmark",
    "scrollToBottom": "fa-solid fa-angles-down",
    "selectSample": {
        "common": " fa-solid",
    },
    "settings": "fa-solid fa-screwdriver-wrench",
    "shuffle": "fa-solid fa-shuffle",
    "sortAlphabet": "fa-solid fa-arrow-down-a-z",
    "sortCalendar": "fa-solid fa-calendar-days",
    "sortNumber": "fa-solid fa-arrow-down-1-9",
    "toggleHeaderNav": "fa-solid fa-ellipsis-vertical",
    "toggleTree": "fa-solid fa-folder-tree",
    "trash": "fa-solid fa-trash-can",
    "upload": "fa-solid fa-cloud-arrow-up",
    "user": "fa-solid fa-user",
    "visible": "fa-eye",
}

icons_dict = icons_fontawesome
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
