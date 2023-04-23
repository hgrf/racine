from flask import abort, jsonify, redirect, render_template, request, send_file
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import not_
from werkzeug.security import safe_join

from . import main
from .forms import NewSampleForm, MarkAsNewsForm
from ..models import Sample, Share, User


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
    return render_template("help.html", admins=admins)


@main.route("/userlist", methods=["POST"])
@login_required
def userlist():
    # get list of all users
    users = User.query.all()

    # determine mode
    mode = request.form.get("mode")
    if mode == "share":
        # get list of people who already share this sample
        sample = Sample.query.get(int(request.form.get("sampleid")))
        sharers = [share.user for share in sample.shares]
        sharers.append(sample.owner)

        # get list of max. 5 people that the current user has recently shared with
        list1 = [
            {"id": share.id, "name": share.user.username}
            for share in Share.query.outerjoin(Sample, Sample.id == Share.sample_id)
            .filter(Sample.owner_id == current_user.id)
            .filter(not_(Share.user_id.in_([x.id for x in sharers])))
            .order_by(Share.id.desc())
            .group_by(Share.user_id)
            .limit(5)
            .all()
        ]

        # get list of max. 5 people that have recently shared with current user
        list2 = [
            {"id": share.id, "name": share.sample.owner.username}
            for share in Share.query.filter(Share.user_id == current_user.id)
            .outerjoin(Sample, Sample.id == Share.sample_id)
            .filter(not_(Sample.owner_id.in_([x.id for x in sharers])))
            .order_by(Share.id.desc())
            .group_by(Sample.owner_id)
            .limit(5)
            .all()
        ]

        # now combine them, order by descending ID, remove duplicates and truncate to 5 elements
        list = sorted(list1 + list2, key=lambda x: x["id"], reverse=True)
        finallist = []
        for i, x in enumerate(list):
            if len(finallist) > 4:
                break
            if x["name"] not in finallist:
                finallist.append(x["name"])

        return jsonify(
            users=[user.username for user in users if user not in sharers], recent=finallist
        )
    elif mode == "leave":
        return jsonify(
            users=[user.username for user in users if user != current_user and user.heir is None]
        )
    else:
        return jsonify(users=[user.username for user in users])


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


@main.route("/plugins/<path:path>")
@login_required
def static_file(path):
    path = safe_join("../plugins/", path)
    if path is None:
        abort(404)
    else:
        return send_file(path)
