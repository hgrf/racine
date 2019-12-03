from flask import render_template, redirect, request, url_for, flash
from .. import db
from ..decorators import admin_required
from ..models import SMBResource, User, Upload, Action, Sample
from forms import NewSMBResourceForm, NewUserForm, EmailSettings
from . import settings
from flask_login import login_required
import git
from config import basedir
from flask import current_app as app
from ..email import send_mail, read_mailconfig
import os
from .. import plugins


@settings.route('/overview')
@login_required
@admin_required
def set_overview():
    return render_template('settings/overview.html')


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
    if request.args.get("delete"):
        user = User.query.filter_by(id=int(request.args.get("delete"))).first()
        db.session.delete(user)
        db.session.commit()
        return redirect('/settings/users')
    form = NewUserForm()
    if form.validate_on_submit():
        user = User(is_admin=form.is_admin.data, email=form.email.data, username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('settings.users'))
    return render_template('settings/users.html', users=User.query.all(), form=form)


@settings.route('/email', methods=['GET', 'POST'])
@login_required
@admin_required
def email():
    form = EmailSettings()

    if form.validate_on_submit():
        # save settings
        try:
            with open('mailconfig.py', 'w') as f:
                f.write(
'''{{
    'MAIL_SENDER': '{}',
    'MAIL_SERVER': '{}',
    'MAIL_PORT': {},
    'MAIL_USE_SSL': {},
    'MAIL_USE_TLS': {},
    'MAIL_USERNAME': '{}',
    'MAIL_PASSWORD': '{}'
}}'''.format(form.sender.data, form.server.data, form.port.data, form.use_ssl.data,
           form.use_tls.data, form.username.data, form.password.data))
        except Exception:
            flash('Could not save settings. Make sure MSM has write privileges in its main directory.')

        # send test mail
        try:
            send_mail([form.sender.data], 'Test mail', body='This is a test mail from MSM.')
        except Exception as e:
            flash('Error: '+str(e))
        else:
            flash('Test message was successfully sent')

    try:
        mailconfig = read_mailconfig()
        form.sender.data = mailconfig['MAIL_SENDER']
        form.server.data = mailconfig['MAIL_SERVER']
        form.port.data = mailconfig['MAIL_PORT']
        form.use_ssl.data = mailconfig['MAIL_USE_SSL']
        form.use_tls.data = mailconfig['MAIL_USE_TLS']
        form.username.data = mailconfig['MAIL_USERNAME']
    except Exception:
        pass

    return render_template('settings/email.html', form=form)


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

    return render_template('settings/revision.html',
                           local_rev=local_revision,
                           remote_rev=remote_revision,
                           recent_changes=recent_changes,
                           plugins=plugins)


### two helper functions for the settings/uploads page
def handle_img(loc, src, refdlist):
    if src[:15] == '/browser/ulimg/':
        #print loc, "uploaded image ID", src[15:]
        refdlist.append(int(src[15:]))
    elif src[:5] == 'data:':
        #print loc, "base64 image"
        pass
    else:
        #print loc, "other source:", src
        pass

def handle_img_tags(text, itemid, refdlist):
    i = -1
    while True:
        i = text.find('<img', i+1)
        if i != -1:
            j = text.find('>', i)   # end of img tag
            k = text.find('src=', i)
            assert k<j                            # make sure the src attr. belongs to the img tag
            l = k+4
            invcomma = text[l]
            m = text.find(invcomma, l+1)
            assert m<j                            # make sure the string ends before the end of the img tag
            handle_img("{} position {}".format(itemid, i), text[l+1:m], refdlist)
        else:
            break

@settings.route('/uploads', methods=['GET'])
@login_required
@admin_required
def uploads():
    ##### Find duplicates and empty files
    # could probably do this much better with an elegant DB query
    uploads = Upload.query.all()
    emptyfiles = []
    nofiles = []
    duplicates = []
    for i1 in range(len(uploads)):
        u1 = uploads[i1]
        # check file size
        try:
            stat = os.stat(os.path.join(app.config['UPLOAD_FOLDER'], str(u1.id) + '.' + u1.ext))
        except:
            nofiles.append(u1)
            continue
        if stat.st_size == 0:
            #print "Upload ID {} is an empty file.".format(u1.id)
            emptyfiles.append(u1)
            continue
        for i2 in range(i1, len(uploads)):  # only iterate through rest of uploads (avoid double counting)
            u2 = uploads[i2]
            if u1.id == u2.id: continue
            if u1.hash == u2.hash:
                #print "Upload ID {} is a duplicate of {}.".format(u1.id, u2.id)
                duplicates.append((u1, u2))

    ##### Scan all referenced images and find unused uploads
    refdlist = []  # list of referenced images
    unused = []     # list of unused uploads

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
            #print "Unused upload: ", u.id
            unused.append(u)

    return render_template('settings/uploads.html', emptyfiles=emptyfiles, nofiles=nofiles, duplicates=duplicates, unused=unused)


@settings.route('/log', methods=['GET'])
@login_required
@admin_required
def log():
    log = 'Failed to load log'
    with open('msm.log', 'r') as f:
        log = f.read()
    return render_template('settings/log.html', log=log)