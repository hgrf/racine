from flask import render_template, redirect, request, url_for, flash, make_response, jsonify
from flask.ext.login import login_user, logout_user, login_required
from . import auth
from ..models import User
from .forms import LoginForm

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

            print request.args.get('next')

            resp = redirect(request.args.get('next') or url_for('main.index'))
        else:
            flash('Incorrect username or password.')
    elif form.is_submitted():
        flash('Please enter a valid username and a password.')

    if not resp:
        resp = make_response(render_template('auth/login.html', form=form,users=User.query.all(),
                                             last_logged_in=last_logged_in))

    resp.set_cookie('last_logged_in', ','.join(last_logged_in))
    return resp

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))
