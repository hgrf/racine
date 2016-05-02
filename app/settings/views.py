from flask import render_template, redirect, request, url_for
from .. import db
from ..decorators import admin_required
from ..models import SampleType
from ..models import ActionType
from ..models import SMBResource
from ..models import User
from forms import NewSMBResourceForm, NewTypeForm, ShutdownForm, NewUserForm
from . import settings
from flask.ext.login import login_required
import git
from config import basedir
from flask import current_app as app

# see http://flask.pocoo.org/snippets/67/
def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@settings.route('/overview')
@login_required
@admin_required
def set_overview():
    return render_template('settings/overview.html')


@settings.route('/sampletypes', methods=['GET', 'POST'])
@login_required
@admin_required
def sampletypes():
    form = NewTypeForm()
    if form.validate_on_submit():
        db.session.add(SampleType(name=form.name.data))
        db.session.commit()
        form.name.data = ''
    return render_template('settings/sampletypes.html', sampletypes=SampleType.query.all(), form=form)


@settings.route('/actiontypes', methods=['GET', 'POST'])
@login_required
@admin_required
def actiontypes():
    form = NewTypeForm()
    if form.validate_on_submit():
        db.session.add(ActionType(name=form.name.data))
        db.session.commit()
        form.name.data = ''
    return render_template('settings/actiontypes.html', actiontypes=ActionType.query.all(), form=form)


@settings.route('/shutdown', methods=['GET', 'POST'])
@login_required
@admin_required
def shutdown():
    form = ShutdownForm()
    if form.validate_on_submit():
        shutdown_server()
        return 'Server shutting down...'
    return render_template('settings/shutdown.html', form=form)


@settings.route('/smbresources', methods=['GET', 'POST'])
@login_required
@admin_required
def smbresources():
    if request.args.get("delete"):
        resource = SMBResource.query.filter_by(id=int(request.args.get("delete"))).first()
        db.session.delete(resource)
        db.session.commit()
        return redirect('/settings/smbresources')
    form = NewSMBResourceForm()
    if form.validate_on_submit():
        db.session.add(
            SMBResource(name=form.name.data, servername=form.servername.data, serveraddr=form.serveraddr.data,
                        sharename=form.sharename.data, path=form.path.data, userid=form.userid.data, password=form.password.data))
        db.session.commit()
        form.name.data = ''
        form.servername.data = ''
        form.serveraddr.data = ''
        form.sharename.data = ''
        form.path.data = ''
        form.userid.data = ''
        form.password.data = ''
    return render_template('settings/smbresources.html', smbresources=SMBResource.query.all(), form=form)


@settings.route('/users', methods=['GET', 'POST'])
@login_required
@admin_required
def users():
    form = NewUserForm()
    if form.validate_on_submit():
        user = User(is_admin=form.is_admin.data, email=form.email.data, username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('settings.users'))
    return render_template('settings/users.html', users=User.query.all(), form=form)


@settings.route('/revision', methods=['GET'])
@login_required
@admin_required
def revision():
    recent_changes = []
    remote_revision = 0
    local_revision = 0
    try:
        repo = git.Repo(basedir)  # get Sample Manager git repo
        local_revision = repo.rev_parse('HEAD')

        maxc = 10
        for c in repo.iter_commits():
            recent_changes.append(c)
            maxc = maxc - 1
            if not maxc:
                break
    except Exception as inst:
        app.logger.error("Could not retrieve local git information:" + str(type(inst)) + str(inst.args))

    # Getting remote info fails if this is run on production server, probably due to a
    # problem getting the right SSH key (and especially getting it unlocked).
    # There are several ways to solve this (e.g. using an open repository, using an SSH
    # key without passphrase or just ignoring this problem and moving all this Git
    # stuff to the admin section).
    try:
        remote = git.remote.Remote(repo, 'origin')  # remote repo
        info = remote.fetch()[0]  # fetch changes
        remote_revision = info.commit  # latest remote commit
    except Exception as inst:
        app.logger.error("Could not retrieve remote git information:" + str(type(inst)) + str(inst.args))

    return render_template('settings/revision.html', local_rev=local_revision, remote_rev=remote_revision, recent_changes=recent_changes)
