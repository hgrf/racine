from flask import render_template, redirect, request, url_for, flash, make_response, jsonify
from flask.ext.login import login_user, logout_user, login_required, current_user
from . import auth
from ..models import User
from .forms import LoginForm, PasswordResetRequestForm, PasswordResetForm
from flask_mail import Mail, Message
from flask import current_app as app
from .. import db


@auth.route('/login', methods=['GET', 'POST'])
def login():
    last_logged_in = request.cookies.get('last_logged_in')
    last_logged_in = last_logged_in.split(',') if last_logged_in else []

    form = LoginForm()
    resp = None
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            # log in the user
            login_user(user, form.remember_me.data)

            # make user first in list of last logged in users and trim the list to 5 users
            while user.username in last_logged_in:
                last_logged_in.remove(user.username)
            last_logged_in.insert(0, user.username)
            last_logged_in = last_logged_in[0:5]

            resp = redirect(request.args.get('next') or url_for('main.index'))
        else:
            flash('Incorrect username or password.')
    elif form.is_submitted():
        flash('Please enter a valid username and a password.')

    if not resp:
        resp = make_response(render_template('auth/login.html', form=form,users=User.query.all(),
                                             last_logged_in=last_logged_in))

    resp.set_cookie('last_logged_in', ','.join(last_logged_in), max_age=3600*24*7*4) # 4 week validity for the cookie
    return resp

@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()

            # send password reset mail
            if app.config['MAIL_SERVER'] is None:
                flash('Email support is not correctly set up. Please contact the administrator.')
                return redirect(url_for('auth.login'))
            mail = Mail(app)
            try:
                msg = Message()
                msg = mail.send_message(
                    'Reset your password',
                    sender=('MSM Admin', app.config['MAIL_SENDER']),
                    recipients=[user.email],
                    body=render_template('auth/email/reset_password.txt', user=user, token=token, next=request.args.get('next'))
                )
            except Exception as e:
                flash('Error: ' + str(e))
            else:
                flash('An email with instructions to reset your password has been sent to you.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        if User.reset_password(token, form.password.data):
            db.session.commit()
            flash('Your password has been updated.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))
