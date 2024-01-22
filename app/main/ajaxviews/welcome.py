import ctypes
import os
import platform

from datetime import date, datetime, timedelta
from flask import current_app, render_template
from flask_login import current_user, login_required
from sqlalchemy.sql import func

from . import ajaxviews
from ...smbinterface import smbinterface
from ...common import db
from ...models import Action, Activity, Upload, User, Sample


@ajaxviews.route("/welcome")
@login_required
def welcome():
    # get free disk space
    if platform.system() == "Windows":
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(
            ctypes.c_wchar_p(os.getcwd()), None, None, ctypes.pointer(free_bytes)
        )
        availablevol = free_bytes.value
    else:
        statvfs = os.statvfs(os.getcwd())
        availablevol = statvfs.f_bavail * statvfs.f_frsize

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
        .filter(Activity.user_id == current_user.id, Sample.isdeleted == False)  # noqa: E712
        .order_by(Activity.id.desc())
        .distinct()
        .limit(5)
        .all()
    )

    # remove samples that are not shared with the user anymore
    # NB: this might reduce the recent_samples list to less than five elements
    recent_samples = [s for s in recent_samples if s.is_accessible_for(current_user)]

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
        icons=current_app.config["ICONS"],
        conns=smbinterface.conns,
        recent_samples=recent_samples,
        newactionsallusers=newactionsallusers,
        maxcountallusers=maxcountallusers,
        uploadvols=uploadvols,
        maxuploadvol=maxuploadvol,
        totuploadvol=totuploadvol,
        availablevol=availablevol,
        dbsize=dbsize,
        news=news,
    )
