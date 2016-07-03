from flask import render_template, redirect, request, url_for
from . import profile
from .. import db
from flask.ext.login import login_required, current_user
from forms import ChangePasswordForm, ChangeDetailsForm
from ..models import User

@profile.route('/overview')
@login_required
def overview():
    return render_template('profile/overview.html')


@profile.route('/changedetails', methods=['GET', 'POST'])
@login_required
def changedetails():
    form = ChangeDetailsForm()
    if form.validate_on_submit():
        user = current_user
        if(user.verify_password(form.password.data)):
            user.username = form.username.data
            user.email = form.email.data
            db.session.commit()
            return redirect('/')
        else:
            flash('Password incorrect.')
    return render_template('profile/changedetails.html', form=form)

@profile.route('/changepassword', methods=['GET', 'POST'])
@login_required
def changepassword():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user = current_user
        if(user.verify_password(form.oldpassword.data)):
            user.password = form.password.data
            db.session.commit()
            return redirect('/')
        else:
            flash('Password incorrect.')
    return render_template('profile/changepassword.html', form=form)


@profile.route('/leave', methods=['GET'])
@login_required
def leave():
    users = User.query.all()
    user = User.query.filter_by(id=request.args.get("userid")).first()
    confirm = request.args.get("confirm")
    reactivate = request.args.get("reactivate")

    if reactivate == "1":
        current_user.heir = None
        db.session.commit()

    if confirm == "1" and user is not None:
        current_user.heir = user
        db.session.commit()

    return render_template('profile/leave.html', users=users, user=user)