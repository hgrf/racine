from flask import abort, jsonify, redirect, render_template, request, send_file
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import not_
from werkzeug.security import safe_join

from . import main
from .forms import NewSampleForm, MarkActionAsNewsForm
from ..models import (
    Sample,
    User,
    Share,
    search_tree,
)


@main.route("/")
@login_required
def index():
    return render_template(
        "main/main.html",
        view="main",
        params={"ajaxView": "welcome"},
        api_token=current_user.get_token(),
        newsampleform=NewSampleForm(),
        dlg_markasnews_form=MarkActionAsNewsForm(),
    )


@main.route("/sample/<int:sampleid>")
@login_required
def sample(sampleid):
    sample = Sample.query.get(sampleid)
    if sample is None or not sample.is_accessible_for(current_user) or sample.isdeleted:
        return render_template("errors/404.html"), 404
    return render_template(
        "main/main.html",
        view="main",
        params={"ajaxView": "sample", "sampleid": sampleid},
        api_token=current_user.get_token(),
        newsampleform=NewSampleForm(),
        dlg_markasnews_form=MarkActionAsNewsForm(),
    )


@main.route("/help")
@login_required
def help():
    admins = User.query.filter_by(is_admin=True).all()
    return render_template("help.html", admins=admins)


@main.route("/search", methods=["GET"])
@login_required
def search():
    keyword = request.args.get("term")
    if keyword is None or keyword == "":
        return jsonify(error="Please specify a search term")

    results = [
        {
            "name": sample.name,
            "id": sample.id,
            "ownername": sample.owner.username,
            "mysample": (sample.owner == current_user),
            "parentname": sample.parent.name if sample.parent_id else "",
        }
        for sample in search_tree(
            user=current_user,
            query=keyword,
            limit=10,
        )
    ]

    if request.args.get("autocomplete") is not None:
        return jsonify(results=results)
    elif request.args.get("ajax") is not None:
        return render_template("main/searchresults.html", results=results, term=keyword)
    else:
        return render_template(
            "main/main.html",
            view="main",
            params={"ajaxView": "searchResults", "term": keyword},
            sample=None,
            term=keyword,
            newsampleform=NewSampleForm(),
            dlg_markasnews_form=MarkActionAsNewsForm(),
        )


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
