import os

from datetime import date, datetime, timedelta
from flask import abort, current_app, jsonify, redirect, render_template, request, send_file
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import not_
from sqlalchemy.sql import func
from werkzeug.security import safe_join

from . import main
from .forms import NewSampleForm, NewActionForm, MarkActionAsNewsForm
from .. import db, plugins, smbinterface
from ..models import (
    Sample,
    Action,
    User,
    Share,
    Upload,
    Activity,
)


@main.route("/")
@main.route("/sample/<int:sampleid>")
def index(sampleid=0):
    if not current_user.is_authenticated:
        return redirect("/auth/login?next=%2F")

    # TODO: reduce redundance in call to render_template
    if not sampleid:
        return render_template(
            "main/main.html",
            state={"view": "welcome", "url": "/"},
            api_token=current_user.get_token(),
            newsampleform=NewSampleForm(),
            dlg_markasnews_form=MarkActionAsNewsForm(),
        )
    sample = Sample.query.get(sampleid)
    if sample is None or not sample.is_accessible_for(current_user) or sample.isdeleted:
        return render_template("errors/404.html"), 404
    return render_template(
        "main/main.html",
        state={"view": "sample", "sampleid": sampleid, "url": "/sample/{}".format(sampleid)},
        api_token=current_user.get_token(),
        newsampleform=NewSampleForm(),
        dlg_markasnews_form=MarkActionAsNewsForm(),
    )


@main.route("/welcome")
@login_required
def welcome():
    # get free disk space
    statvfs = os.statvfs(os.path.dirname(__file__))
    availablevol = statvfs.f_frsize * statvfs.f_bavail

    # get size of the SQLite database
    dbsize = os.path.getsize(current_app.config["SQLALCHEMY_DATABASE_URI"][10:])

    # get user activity for all users (only admin will see this)
    aweekago = date.today() - timedelta(weeks=1)
    stmt = (
        db.session.query(Action.owner_id, func.count("*").label("action_count"))
        .filter(Action.datecreated > aweekago)
        .group_by(Action.owner_id)
        .subquery()
    )
    user_vs_count = (
        db.session.query(User, stmt.c.action_count)
        .outerjoin(stmt, User.id == stmt.c.owner_id)
        .order_by(User.id)
        .all()
    )
    newactionsallusers = []
    maxcountallusers = 0
    for n in user_vs_count:
        if n[1] is not None:
            newactionsallusers.append(n)
            maxcountallusers = max(maxcountallusers, n[1])

    # get per user upload volume for all users (only admin will see this)
    stmt = (
        db.session.query(Upload.user_id, func.sum(Upload.size).label("upload_volume"))
        .group_by(Upload.user_id)
        .subquery()
    )
    uploadvols = (
        db.session.query(User, stmt.c.upload_volume)
        .outerjoin(stmt, User.id == stmt.c.user_id)
        .order_by(User.id)
        .all()
    )
    maxuploadvol = 0
    totuploadvol = 0
    for u in uploadvols:
        maxuploadvol = max(maxuploadvol, u[1] if u[1] is not None else 0)
        totuploadvol += u[1] if u[1] is not None else 0

    # get last modified samples
    recent_samples = (
        db.session.query(Sample)
        .join(Activity)
        .filter(Activity.user_id == current_user.id, not Sample.isdeleted)
        .order_by(Activity.id.desc())
        .distinct()
        .limit(5)
        .all()
    )

    # remove samples that are not shared with the user anymore
    # NB: this might reduce the recent_samples list to less than five elements
    recent_samples = [s for s in recent_samples if s.is_accessible_for(current_user)]

    # execute plugin display functions
    plugin_display = []
    for p in plugins:
        try:
            display = p.display()
        except Exception:
            display = "Error in plugin"
        plugin_display.append([p.title, display])

    # assemble news
    news = [link.news for link in current_user.news_links]
    news = sorted(news, key=lambda n: n.id, reverse=True)

    # check for expired news
    expired = []
    not_expired = []
    for n in news:
        if datetime.today().date() > n.expires:
            expired.append(n)
            db.session.delete(n)
        else:
            not_expired.append(n)
    db.session.commit()
    news = not_expired

    return render_template(
        "main/welcome.html",
        conns=smbinterface.conns,
        recent_samples=recent_samples,
        newactionsallusers=newactionsallusers,
        maxcountallusers=maxcountallusers,
        uploadvols=uploadvols,
        maxuploadvol=maxuploadvol,
        plugin_display=plugin_display,
        totuploadvol=totuploadvol,
        availablevol=availablevol,
        dbsize=dbsize,
        news=news,
    )


@main.route("/navbar", methods=["GET"])
@login_required
def navbar():
    inheritance = User.query.filter_by(heir=current_user).all()
    showarchived = (
        True
        if request.args.get("showarchived") is not None
        and request.args.get("showarchived") == "true"
        else False
    )
    order = request.args.get("order") if request.args.get("order") else "id"

    # only query root level samples, the template will build the hierarchy
    samples = Sample.query.filter_by(owner=current_user, parent_id=0, isdeleted=False).all()
    samples.extend(current_user.directshares)

    return render_template(
        "main/navbar.html",
        samples=samples,
        inheritance=inheritance,
        showarchived=showarchived,
        order=order,
    )


@main.route("/editor/<sampleid>", methods=["GET", "POST"])
@login_required
def editor(sampleid):
    sample = Sample.query.get(sampleid)
    shares = sample.shares
    showparentactions = (
        True
        if request.args.get("showparentactions") is not None
        and request.args.get("showparentactions") == "true"
        else False
    )
    invertactionorder = (
        True
        if request.args.get("invertactionorder") is not None
        and request.args.get("invertactionorder") == "true"
        else False
    )

    if sample is None or not sample.is_accessible_for(current_user) or sample.isdeleted:
        return render_template("errors/404.html"), 404
    else:
        form = NewActionForm()
        form.description.data = ""
        form.timestamp.data = date.today()

        # ----- get actions for this sample and all parent samples and order them by ordnum
        actions = []
        s = sample
        while s is not None:
            actions.extend(Action.query.filter_by(sample=s).order_by(Action.ordnum).all())
            s = s.parent
            if not showparentactions:
                break
        actions = sorted(actions, key=lambda a: a.ordnum, reverse=invertactionorder)

        return render_template(
            "main/editor.html",
            sample=sample,
            actions=actions,
            form=form,
            shares=shares,
            showparentactions=showparentactions,
            invertactionorder=invertactionorder,
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
    keyword = keyword.lower()

    # In order to reach really ALL samples that are accessible by the current user, we need to
    # go through the hierarchy. The most tricky samples to catch are the children of a sample
    # that the user shares with someone else and that are not explicitly shared with the user.
    #
    # The problem with the following strategy is that samples on the same hierarchy level are
    # not given the same priority in the results list. Instead the first "tree" will be given
    # highest priority.
    def find_in(samples, keyword, limit):
        if not samples or limit < 1:
            return []
        result = []
        for s in samples:
            # sample name should never be None, but due to bugs this may happen...
            if s.name is not None and keyword in s.name.lower():
                result.append(s)
            # TODO: does s.children contain deleted samples ?
            result.extend(find_in(s.children + s.mountedsamples, keyword, limit - len(result)))
        return result

    own_samples = Sample.query.filter_by(owner=current_user, parent_id=0, isdeleted=False).all()
    shares = current_user.directshares
    results = [
        {
            "name": s.name,
            "id": s.id,
            "ownername": s.owner.username,
            "mysample": (s.owner == current_user),
            "parentname": s.parent.name if s.parent_id else "",
        }
        for s in find_in(own_samples + shares, keyword, 10)
    ]

    if request.args.get("autocomplete") is not None:
        return jsonify(results=results)
    elif request.args.get("ajax") is not None:
        return render_template("main/searchresults.html", results=results, term=keyword)
    else:
        return render_template(
            "main/main.html",
            state={"view": "searchResults", "term": keyword, "url": "/search?term=" + keyword},
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
