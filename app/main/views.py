from flask import jsonify, redirect, render_template, request
from flask_login import current_user, login_required, login_user, logout_user

from . import main
from .forms import NewSampleForm, MarkAsNewsForm
from ..version import RACINE_VERSION
from ..models import Sample, User


def render_main_template(**params):
    return render_template(
        "main/main.html",
        view="main",
        api_token=current_user.get_token(),
        newsampleform=NewSampleForm(),
        markasnewsform=MarkAsNewsForm(),
        params=params,
    )


@main.route("/")
@login_required
def index():
    return render_main_template(ajaxView="welcome")


@main.route("/sample/<int:sampleid>")
@login_required
def sample(sampleid):
    sample = Sample.query.get(sampleid)
    if sample is None or not sample.is_accessible_for(current_user) or sample.isdeleted:
        return render_template("errors/404.html"), 404
    return render_main_template(ajaxView="sample", sampleid=sampleid)


@main.route("/search", methods=["GET"])
@login_required
def search():
    keyword = request.args.get("term")
    if keyword is None or keyword == "":
        return jsonify(error="Please specify a search term")

    return render_main_template(ajaxView="searchResults", term=keyword)


@main.route("/help")
@login_required
def help():
    admins = User.query.filter_by(is_admin=True).all()
    return render_template("help.html", admins=admins, racine_version=RACINE_VERSION)


@main.route("/loginas", methods=["GET"])
@login_required
def login_as():
    user = User.query.get(int(request.args.get("userid")))

    # check if current user has the right to do this
    if not current_user.is_admin and user.heir != current_user:
        return "You do not have the permission to log in as: " + user.username

    logout_user()
    login_user(user)

    return redirect("/")
