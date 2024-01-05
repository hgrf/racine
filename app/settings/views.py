import os
import redis

from flask import current_app as app, flash, jsonify, render_template, redirect, request
from flask_login import current_user, login_required

from . import settings
from .forms import NewSMBResourceForm, NewUserForm, EmailSettings, UsageStatsSettings
from ..common import db
from ..decorators import admin_required
from ..emailing import send_mail, read_mailconfig, write_mailconfig
from ..models import SMBResource, User, Upload, Action, Sample


@settings.route("/smbresources", methods=["GET"])
@login_required
@admin_required
def smbresources():
    return render_template(
        "settings/smbresources.html",
        api_token=current_user.get_token(),
        smbresources=SMBResource.query.all(),
        form=NewSMBResourceForm(),
    )


@settings.route("/users", methods=["GET"])
@login_required
@admin_required
def users():
    return render_template(
        "settings/users.html",
        api_token=current_user.get_token(),
        users=User.query.all(),
        form=NewUserForm(),
    )


@settings.route("/email", methods=["GET", "POST"])
@login_required
@admin_required
def email():
    form = EmailSettings()
    task = None

    if form.validate_on_submit():
        # save settings
        try:
            write_mailconfig(form)
        except Exception:
            flash(
                "Could not save settings. Make sure Racine has write privileges in its "
                + "main directory."
            )

        # send test mail
        task = send_mail([form.sender.data], "Test mail", body="This is a test mail from Racine.")

    try:
        read_mailconfig(form)
    except Exception:
        pass

    return (
        render_template("settings/email.html", api_token=current_user.get_token(), form=form)
        if task is None
        else jsonify({"task_id": task.id}),
        200 if task is None else 202,
    )


@settings.route("/stats", methods=["GET", "POST"])
@login_required
@admin_required
def stats():
    form = UsageStatsSettings()
    if form.validate_on_submit():
        with open("data/usage_stats_site", "w") as f:
            f.write(form.site.data)
        flash("Saved changes")

    try:
        with open("data/usage_stats_key") as f:
            form.key.data = f.read()
        with open("data/usage_stats_site") as f:
            form.site.data = f.read()
    except Exception:
        pass

    r = redis.Redis(host="racine-redis", port=6379, decode_responses=True)
    stats = r.get("usage-stats")
    if stats is None:
        stats = "No usage statistics transmitted yet."
    return render_template("settings/stats.html", form=form, stats=stats)


# ----- two helper functions for the settings/uploads page
def handle_img(loc, src, refdlist):
    if src[:15] == "/browser/ulimg/":
        # print loc, "uploaded image ID", src[15:]
        refdlist.append(int(src[15:]))
    elif src[:5] == "data:":
        # print loc, "base64 image"
        pass
    else:
        # print loc, "other source:", src
        pass


def handle_img_tags(text, itemid, refdlist):
    i = -1
    while True:
        i = text.find("<img", i + 1)
        if i != -1:
            j = text.find(">", i)  # end of img tag
            k = text.find("src=", i)
            assert k < j  # make sure the src attr. belongs to the img tag
            z = k + 4
            invcomma = text[z]
            m = text.find(invcomma, z + 1)
            assert m < j  # make sure the string ends before the end of the img tag
            handle_img("{} position {}".format(itemid, i), text[z + 1 : m], refdlist)
        else:
            break


@settings.route("/uploads", methods=["GET"])
@login_required
@admin_required
def uploads():  # noqa: C901 (ignore complexity, this function is not used in production)
    # ----- Find duplicates and empty files
    # could probably do this much better with an elegant DB query
    uploads = Upload.query.all()
    emptyfiles = []
    nofiles = []
    duplicates = []
    for i1 in range(len(uploads)):
        u1 = uploads[i1]
        # check file size
        try:
            stat = os.stat(os.path.join(app.config["UPLOAD_FOLDER"], str(u1.id) + "." + u1.ext))
        except Exception:
            nofiles.append(u1)
            continue
        if stat.st_size == 0:
            # print "Upload ID {} is an empty file.".format(u1.id)
            emptyfiles.append(u1)
            continue
        for i2 in range(
            i1, len(uploads)
        ):  # only iterate through rest of uploads (avoid double counting)
            u2 = uploads[i2]
            if u1.id == u2.id:
                continue
            if u1.hash == u2.hash:
                # print "Upload ID {} is a duplicate of {}.".format(u1.id, u2.id)
                duplicates.append((u1, u2))

    # ----- Scan all referenced images and find unused uploads
    refdlist = []  # list of referenced images
    unused = []  # list of unused uploads

    # check for image tags in action descriptions
    actions = Action.query.all()
    for action in actions:
        handle_img_tags(action.description, "action {}".format(action.id), refdlist)

    # check for sample images and image tags in sample descriptions
    samples = Sample.query.all()
    for sample in samples:
        if sample.image is not None:
            handle_img("sample {}".format(sample.id), sample.image, refdlist)
        if sample.description is not None:
            handle_img_tags(sample.description, "sample {}".format(sample.id), refdlist)

    # find unused uploads
    uploads = Upload.query.all()
    for u in uploads:
        if u.id not in refdlist:
            # print "Unused upload: ", u.id
            unused.append(u)

    return render_template(
        "settings/uploads.html",
        emptyfiles=emptyfiles,
        nofiles=nofiles,
        duplicates=duplicates,
        unused=unused,
    )


@settings.route("/log", methods=["GET"])
@login_required
@admin_required
def log():
    log = "Failed to load log"
    with open("data/racine.log", "r") as f:
        log = f.read()
    return render_template("settings/log.html", log=log)
