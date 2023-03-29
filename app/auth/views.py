from flask import render_template, redirect, request, url_for, flash, make_response, session
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from ..models import User, record_activity
from .forms import LoginForm, PasswordResetRequestForm, PasswordResetForm
from .. import db
from ..emailing import send_mail


@auth.route("/login", methods=["GET", "POST"])
def login():
    last_logged_in = request.cookies.get("last_logins")
    last_logged_in = last_logged_in.split(",") if last_logged_in else []

    # workaround to avoid server error when trying to connect with cookie from python 2 version
    try:
        form = LoginForm()
    except TypeError:
        # erroneous cookie for testing:
        # session = eyJjc3JmX3Rva2VuIjp7IiBiIjoiT1RKaE4yTmpaRGc0WXpNMl
        #           pqZGhPR1ZoTkRSa1lURmxaRGN5TjJZeU1EZzVObUZsT0ROa1pB
        #           PT0ifX0.XeZ16g.Y3yco4lf1Ofku9GH_vj4ETg2itk
        session.pop("csrf_token")
        form = LoginForm()
    resp = None
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            # log in the user
            login_user(user, form.remember_me.data)

            # log activity
            record_activity("login", current_user, commit=True)

            # make user first in list of last logged in users and trim the list to 5 users
            while str(user.id) in last_logged_in:
                last_logged_in.remove(str(user.id))
            last_logged_in.insert(0, str(user.id))
            last_logged_in = last_logged_in[0:5]

            resp = redirect(request.args.get("next") or url_for("main.index"))
        else:
            flash("Incorrect username or password.")
    elif form.is_submitted():
        flash("Please enter a valid username and a password.")

    last_logged_in_names = []
    for user_id in last_logged_in:
        user = User.query.get(user_id)
        if user:
            last_logged_in_names.append(user.username)

    if not resp:
        resp = make_response(
            render_template(
                "auth/login.html",
                form=form,
                users=User.query.all(),
                last_logged_in=last_logged_in_names,
            )
        )

    resp.set_cookie(
        "last_logins",
        ",".join(last_logged_in),
        path="/auth/login",  # store only for /auth/login path
        max_age=3600 * 24 * 7 * 4,
    )  # 4 week validity for the cookie

    return resp


@auth.route("/reset", methods=["GET", "POST"])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for("main.index"))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()

            # send password reset mail
            try:
                send_mail(
                    [user.email],
                    "Reset your password",
                    body=render_template("auth/email/reset_password.txt", user=user, token=token),
                )
            except Exception:
                flash("Email could not be sent, please contact the administrator.")
            else:
                flash("An email with instructions to reset your password has been sent to you.")
        else:
            flash("That email address could not be found in the database.")
        return redirect(url_for("auth.login"))
    return render_template("auth/reset_password.html", form=form)


@auth.route("/reset/<token>", methods=["GET", "POST"])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for("main.index"))
    form = PasswordResetForm()
    if form.validate_on_submit():
        if User.reset_password(token, form.password.data):
            db.session.commit()
            flash("Your password has been updated.")
            return redirect(url_for("auth.login"))
        else:
            return redirect(url_for("main.index"))
    return render_template("auth/reset_password.html", form=form)


@auth.route("/logout")
@login_required
def logout():
    # log activity
    record_activity("logout", current_user, commit=True)

    logout_user()
    flash("You have been logged out.")
    return redirect(url_for("main.index"))
