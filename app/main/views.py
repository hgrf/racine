from flask import render_template, redirect, request, jsonify, send_file, abort, current_app
from flask_login import current_user, login_required, login_user, logout_user
from .. import db
from .. import plugins
from ..models import (
    Sample,
    Action,
    User,
    Share,
    Upload,
    SMBResource,
    Activity,
    record_activity,
    News,
)
from . import main
from .forms import NewSampleForm, NewActionForm, MarkActionAsNewsForm
from ..settings.forms import NewUserForm
from datetime import date, datetime, timedelta
from .. import smbinterface
from ..validators import validate_form_field
from sqlalchemy.sql import func
from sqlalchemy import not_
import os
import inspect


@main.route("/")
@main.route("/sample/<sampleid>")
def index(sampleid=0):
    if not current_user.is_authenticated:
        return redirect("/auth/login?next=%2F")

    # TODO: reduce redundance in call to render_template
    if not sampleid:
        return render_template(
            "main.html",
            api_token=current_user.get_token(),
            sample=None,
            search_activated=True,
            newsampleform=NewSampleForm(),
            dlg_markasnews_form=MarkActionAsNewsForm(),
        )
    sample = Sample.query.get(sampleid)
    if sample is None or not sample.is_accessible_for(current_user) or sample.isdeleted:
        return render_template("404.html"), 404
    return render_template(
        "main.html",
        api_token=current_user.get_token(),
        sample=sample,
        search_activated=True,
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
        .filter(Activity.user_id == current_user.id, Sample.isdeleted == False)
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
        "welcome.html",
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
        "navbar.html",
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
        return render_template("404.html"), 404
    else:
        form = NewActionForm()
        form.description.data = ""
        form.timestamp.data = date.today()

        ##### get actions for this sample and all parent samples and order them by ordnum
        actions = []
        s = sample
        while s is not None:
            actions.extend(Action.query.filter_by(sample=s).order_by(Action.ordnum).all())
            s = s.parent
            if not showparentactions:
                break
        actions = sorted(actions, key=lambda a: a.ordnum, reverse=invertactionorder)

        return render_template(
            "editor.html",
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
    # In order to reach really ALL samples that are accessible by the current user, we need to go through the hierarchy.
    # The most tricky samples to catch are the children of a sample that the user shares with someone else and that are
    # not explicitly shared with the user.
    #
    # The problem with the following strategy is that samples on the same hierarchy level are not given the same
    # priority in the results list. Instead the first "tree" will be given highest priority.
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
        return render_template("searchresults.html", results=results, term=keyword)
    else:
        return render_template(
            "main.html",
            sample=None,
            search_activated=True,
            term=keyword,
            newsampleform=NewSampleForm(),
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


@main.route("/togglearchived", methods=["POST"])
@login_required
def togglearchived():
    sample = Sample.query.get(int(request.form.get("id")))
    if sample is None or sample.owner != current_user or sample.isdeleted:
        return jsonify(
            code=1, error="Sample does not exist or you do not have the right to access it"
        )
    sample.isarchived = not sample.isarchived
    db.session.commit()
    return jsonify(code=0, isarchived=sample.isarchived)


@main.route("/togglecollaborative", methods=["POST"])
@login_required
def togglecollaborative():
    sample = Sample.query.get(int(request.form.get("id")))
    if sample is None or sample.owner != current_user or sample.isdeleted:
        return jsonify(
            code=1, error="Sample does not exist or you do not have the right to access it"
        )
    sample.iscollaborative = not sample.iscollaborative
    db.session.commit()
    return jsonify(code=0, iscollaborative=sample.iscollaborative)


@main.route("/createshare", methods=["POST"])
@login_required
def createshare():
    sample = Sample.query.get(int(request.form.get("sampleid")))
    user = None
    if request.form.get("userid"):
        user = User.query.get(int(request.form.get("userid")))
    elif request.form.get("username"):
        user = User.query.filter_by(username=(request.form.get("username"))).first()
    if user is None:
        return jsonify(code=1, error="No valid user ID or name given"), 500
    if sample is None or sample.owner != current_user or sample.isdeleted:
        return (
            jsonify(
                code=1, error="Sample does not exist or you do not have the right to access it"
            ),
            500,
        )
    if user in [x.user for x in sample.shares]:
        return jsonify(code=1, error="This share already exists"), 500
    share = Share(sample=sample, user=user, mountpoint_id=0)
    db.session.add(share)
    record_activity("add:share", current_user, sample)
    db.session.commit()

    # re-dispatch news for this sample and for all children
    affected_samples = [sample]
    while affected_samples:
        s = affected_samples.pop()
        affected_samples.extend(s.children)
        news = News.query.filter_by(sample_id=s.id).all()
        for n in news:
            n.dispatch()

    return jsonify(code=0, username=user.username, userid=user.id, shareid=share.id)


@main.route("/changeparent", methods=["POST"])
@login_required
def changeparent():
    sample = Sample.query.get(int(request.form.get("id")))
    if sample is None or not sample.is_accessible_for(current_user) or sample.isdeleted:
        return jsonify(
            code=1, error="Sample does not exist or you do not have the right to access it"
        )

    # check if we're not trying to make the snake bite its tail
    parentid = int(request.form.get("parent"))
    if parentid != 0:
        p = Sample.query.filter_by(id=parentid).first()
        while p.logical_parent:
            if p.logical_parent == sample:
                return jsonify(code=1, error="Cannot move sample")
            p = p.logical_parent

    # check if the current user is the sample owner, otherwise get corresponding share
    if sample.owner != current_user:
        if sample.is_accessible_for(current_user, indirect_only=True):
            return jsonify(
                code=1,
                error="The sample owner ("
                + sample.owner.username
                + ") has fixed the sample's location.",
            )

        share = Share.query.filter_by(sample=sample, user=current_user).first()
        if share is None:
            return jsonify(code=1, error="Could not find corresponding share")
        try:
            share.mountpoint_id = parentid
            db.session.commit()
        except Exception as e:
            return jsonify(code=1, error="Exception: " + str(e))
    else:
        # change parent ID
        try:
            sample.parent_id = parentid
            db.session.commit()

            # re-dispatch news for this sample and for all children
            affected_samples = [sample]
            while affected_samples:
                s = affected_samples.pop()
                affected_samples.extend(s.children)
                news = News.query.filter_by(sample_id=s.id).all()
                for n in news:
                    n.dispatch()
        except Exception as e:
            return jsonify(code=1, error=str(e))
    return jsonify(code=0)


@main.route("/newsample", methods=["POST"])
@login_required
def newsample():
    form = NewSampleForm()
    if form.validate_on_submit():
        try:
            parent_id = int(form.newsampleparentid.data) if form.newsampleparentid.data else 0
            sample = Sample(
                owner=current_user,
                name=form.newsamplename.data,
                parent_id=parent_id,
                description=form.newsampledescription.data,
                isarchived=False,
                isdeleted=False,
            )
            db.session.add(sample)
            db.session.commit()
            record_activity("add:sample", current_user, sample, commit=True)
            return jsonify(code=0, sampleid=sample.id)
        except Exception as e:
            db.session.rollback()
            return jsonify(code=1, error={"newsamplename": [str(e)]})
    elif form.is_submitted():
        return jsonify(code=1, error={field: errors for field, errors in form.errors.items()})
    abort(500)  # this should never happen


@main.route("/markasnews", methods=["POST"])
@login_required
def markasnews():
    form = MarkActionAsNewsForm()
    if form.validate_on_submit():
        # get action from database
        action = Action.query.get(form.action_id.data)
        if action is None:
            return jsonify(code=1, error="Action does not exist")

        # check if action is already marked as news
        if action.news_id:
            return jsonify(code=1, error="Action is already marked as news")

        # mark action as news
        news = News(
            sender_id=current_user.id,
            sample_id=action.sample_id,
            title=form.title.data,
            content="action:{}".format(action.id),
            published=datetime.today(),
            expires=form.expires.data,
        )
        db.session.add(news)
        db.session.commit()
        action.news_id = news.id
        db.session.commit()

        news.dispatch()

        return jsonify(code=0)
    elif form.is_submitted():
        return jsonify(code=1, error={field: errors for field, errors in form.errors.items()})
    abort(500)  # this should never happen


@main.route("/unmarkasnews", methods=["POST"])
@login_required
def unmarkasnews():
    action = Action.query.get(request.form.get("actionid"))
    if action is None:
        return jsonify(code=1, error="Action does not exist")

    # check if action is really marked as news
    if not action.news_id:
        return jsonify(code=1, error="Action is not marked as news")

    if action.news.sender != current_user:
        return jsonify(
            code=1,
            error="Only the sender of the news ({}) can unmark this action as news".format(
                action.news.sender.username
            ),
        )

    # by cascade deletion, this will also remove all corresponding items from the linkusernews table
    db.session.delete(action.news)

    # unmark action as news
    # TODO: record activity
    action.news_id = None
    db.session.commit()

    return jsonify(code=0)


@main.route("/newaction/<sampleid>", methods=["POST"])
@login_required
def newaction(sampleid):
    sample = Sample.query.get(int(sampleid))
    if sample is None or not sample.is_accessible_for(current_user) or sample.isdeleted:
        return jsonify(
            code=1, error="Sample does not exist or you do not have the right to access it"
        )

    form = NewActionForm()
    if form.validate_on_submit():
        a = Action(
            datecreated=date.today(),
            timestamp=form.timestamp.data,
            owner=current_user,
            sample_id=sampleid,
            description=form.description.data,
        )
        db.session.add(a)
        record_activity("add:action", current_user, sample)
        db.session.commit()
        a.ordnum = a.id  # add ID as order number (maybe there is a more elegant way to do this?)
        db.session.commit()
    # if form was submitted but failed validation, show again to user
    # this is very important for the case where form is not validated because the
    # CSRF token passed its time limit (typically 3600s) -> users lose everything they
    # wrote otherwise (also happens when user enters invalid date)
    elif form.is_submitted():
        return jsonify(code=1, description=form.description.data)

    return jsonify(code=0)


@main.route("/swapactionorder", methods=["POST"])
@login_required
def swapactionorder():  # TODO: sort out permissions for this (e.g. who has the right to change order?)
    action = Action.query.get(int(request.form.get("actionid")))
    swapaction = Action.query.get(int(request.form.get("swapid")))
    ordnum = action.ordnum
    action.ordnum = swapaction.ordnum
    swapaction.ordnum = ordnum
    db.session.commit()
    return ""


@main.route("/plugins/<path:path>")
@login_required
def static_file(path):
    # TODO: this looks a bit unsafe to me
    return send_file("../plugins/" + path)


def str_to_bool(str):
    if str.lower() == "true" or str == "1":
        return True
    elif str.lower() == "false" or str == "0":
        return False
    else:
        raise Exception("String could not be converted to boolean")


def validate_is_admin(str, item):
    b = str_to_bool(str)
    if item.is_admin and not b:
        # check if any other administrators are left
        if len(User.query.filter_by(is_admin=True).all()) == 1:
            raise Exception("There has to be at least one administrator.")
    return b


# define supported fields
supported_targets = {
    "sample": {
        "dbobject": Sample,
        "auth": "owner",
        "fields": {
            "name": lambda x: validate_form_field(NewSampleForm(), "newsamplename", x),
            "description": str,
            "image": str,
        },
    },
    "action": {
        "dbobject": Action,
        "auth": "action_auth",
        "fields": {"timestamp": lambda x: datetime.strptime(x, "%Y-%m-%d"), "description": str},
    },
    "share": {"dbobject": Share, "auth": None, "fields": {}},
    "smbresource": {
        "dbobject": SMBResource,
        "auth": "admin",
        "fields": {
            "name": str,
            "servername": str,
            "serveraddr": str,
            "sharename": str,
            "path": str,
            "userid": str,
            "password": str,
        },
    },
    "user": {
        "dbobject": User,
        "auth": "admin",
        "fields": {
            "username": lambda x: validate_form_field(NewUserForm(), "username", x),
            "email": lambda x: validate_form_field(NewUserForm(), "email", x),
            "is_admin": validate_is_admin,
        },
    },
}

# TODO: both getfield and setfield should check if the sample is marked as deleted


@main.route("/get/<target>/<field>/<id>", methods=["GET"])
@login_required
def getfield(target, field, id):
    if not (id and target and field and target in supported_targets):
        return jsonify(code=1)

    # redefine target to simplify
    target = supported_targets[target]

    # try to get requested item from database
    item = target["dbobject"].query.get(id)

    # check if the item is valid and if the requested field is supported
    if not (item and field in target["fields"]):
        return jsonify(code=1)

    # check if the current user is authorized to access this item
    if (
        not (target["auth"] == "owner" and item.owner == current_user)
        and not (target["auth"] == "admin" and current_user.is_admin)
        and not (target["auth"] == "action_auth" and item.has_read_access(current_user))
    ):
        return jsonify(code=1)

    # return value
    if request.args.get("plain") is not None:
        return str(getattr(item, field))
    else:
        return jsonify(code=0, value=getattr(item, field))


@main.route("/set/<target>/<field>/<id>", methods=["POST"])
@login_required
def updatefield(target, field, id):
    if not (id and target and field and target in supported_targets):
        return jsonify(code=1, value="", message="Invalid request")

    value = request.form.get("value")

    # redefine target to simplify
    target_name = target
    target = supported_targets[target]

    # try to get requested item from database
    item = target["dbobject"].query.get(id)

    # check if the item is valid and if the requested field is supported
    if not (item and field in target["fields"]):
        return jsonify(code=1, value="", message="Invalid request")

    # check if the current user is authorized to access this item
    if (
        not (target["auth"] == "owner" and item.owner == current_user)
        and not (target["auth"] == "admin" and current_user.is_admin)
        and not (target["auth"] == "action_auth" and item.has_write_access(current_user))
    ):
        return jsonify(code=1, value="", message="Invalid request")

    # try to assign value
    try:
        # check if a modifier is to be applied
        modifier = target["fields"][field]
        if modifier is None:
            setvalue = value
        # check if the modifier is a function
        elif type(modifier) == type(lambda x: x):
            argno = len(inspect.getargspec(modifier).args)
            if argno == 1:
                setvalue = modifier(value)
            elif argno == 2:
                setvalue = modifier(value, item)
            elif argno == 3:
                setvalue = modifier(value, item, field)
            else:
                raise Exception("Invalid modifier")
        # otherwise it is probably simply type casting
        else:
            setvalue = modifier(value)
        if getattr(item, field) != setvalue:
            setattr(item, field, setvalue)
            if target_name == "sample":
                sample = item
            elif target_name == "action":
                sample = item.sample
            else:
                sample = None
            record_activity("update:" + target_name + ":" + field, current_user, sample)

    except Exception as e:
        return jsonify(code=1, value=str(getattr(item, field)), message="Error: " + str(e))

    # commit changes to database
    db.session.commit()
    return jsonify(code=0, value=value)
