from flask import render_template, redirect, request, url_for
from . import profile
from .. import db
from flask.ext.login import login_required, current_user
from forms import ChangePasswordForm, ChangeDetailsForm

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