from flask import render_template, redirect, request, flash
from . import profile
from .. import db
from flask_login import login_required, current_user
from .forms import ChangePasswordForm, ChangeDetailsForm
from ..models import User


@profile.route("/changedetails", methods=["GET", "POST"])
@login_required
def changedetails():
    form = ChangeDetailsForm()
    if form.is_submitted():
        if form.validate():
            current_user.username = form.username.data
            current_user.email = form.email.data
            db.session.commit()
            flash("Details updated.")
    else:
        form.username.data = current_user.username
        form.email.data = current_user.email

    return render_template("profile/changedetails.html", form=form)


@profile.route("/changepassword", methods=["GET", "POST"])
@login_required
def changepassword():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user = current_user
        if user.verify_password(form.oldpassword.data):
            user.password = form.password.data
            db.session.commit()
            return redirect("/")
        else:
            flash("Password incorrect.")
    return render_template("profile/changepassword.html", form=form)


@profile.route("/leave", methods=["GET"])
@login_required
def leave():
    user = None
    heirname = request.args.get("heir")
    if heirname is not None:
        # try to get corresponding user from database
        user = User.query.filter_by(username=heirname).first()
        if user is None or user.heir is not None or user == current_user:
            flash("Please name a valid user that is still part of the laboratory.")
            return render_template("profile/leave.html", user=None)

    confirm = request.args.get("confirm")
    reactivate = request.args.get("reactivate")

    if reactivate == "1":
        current_user.heir = None
        db.session.commit()

    if confirm == "1" and user is not None:
        current_user.heir = user
        inheritance = []
        # need to create a list of inheritance first,
        # because apparently database changes mess up the for-loop
        for u in current_user.inheritance:
            inheritance.append(u)
        for u in inheritance:
            u.heir = user
        db.session.commit()

    return render_template("profile/leave.html", user=user)
