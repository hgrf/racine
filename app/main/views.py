from flask import render_template, redirect, request, jsonify, send_file, flash, send_from_directory
from flask.ext.login import current_user, login_required, login_user, logout_user
from .. import db
from .. import plugins
from ..models import Sample, Action, User, Share, Upload
from ..models import SAMPLE_NAME_LENGTH   # <-- sort this out
from . import main
from forms import NewSampleForm, NewActionForm, NewMatrixForm
from datetime import date, datetime, timedelta
from .. import smbinterface

from sqlalchemy.sql import func


@main.route('/')
def index():
    if current_user.is_authenticated:
        return sample(0)
    else:
        return redirect('/auth/login?next=%2F')


@main.route('/sample/<sampleid>')
@login_required
def sample(sampleid):
    sample = Sample.query.get(sampleid)
    samples = Sample.query.filter_by(owner=current_user).all()
    myshares = Share.query.filter_by(user=current_user).all()
    myinheritance = User.query.filter_by(heir=current_user).all()
    showarchived = True if request.args.get('showarchived') != None and int(request.args.get('showarchived')) else False

    return render_template('main.html', samples=samples, sample=sample, myshares=myshares, myinheritance=myinheritance,
                           showarchived=showarchived)


@main.route('/welcome')
@login_required
def welcome():
    # get user activity for all users (only admin will see this)
    aweekago = date.today()-timedelta(weeks=1)
    stmt = db.session.query(Action.owner_id, func.count('*').label('action_count')).filter(Action.datecreated > aweekago).group_by(Action.owner_id).subquery()
    newactionsallusers = db.session.query(User, stmt.c.action_count).outerjoin(stmt, User.id==stmt.c.owner_id).order_by(User.id).all()
    maxcountallusers = 0
    for n in newactionsallusers: maxcountallusers = max(maxcountallusers, n[1])

    # get per user upload volume for all users (only admin will see this)
    stmt = db.session.query(Upload.user_id, func.sum(Upload.size).label('upload_volume')).group_by(Upload.user_id).subquery()
    uploadvols = db.session.query(User, stmt.c.upload_volume).outerjoin(stmt, User.id==stmt.c.user_id).order_by(User.id).all()
    maxuploadvol = 0
    for u in uploadvols: maxuploadvol = max(maxuploadvol, u[1])

    # get user activity only for current user (every user will see this for his samples)
    stmt = db.session.query(Action.sample_id, func.count('*').label('action_count')).filter(Action.owner_id == current_user.id).filter(Action.datecreated > aweekago).group_by(Action.sample_id).subquery()
    newactions = db.session.query(Sample, stmt.c.action_count).outerjoin(stmt, Sample.id == stmt.c.sample_id).order_by(Sample.id).all()
    maxcount = 0
    for n in newactions: maxcount = max(maxcount, n[1])

    return render_template('welcome.html', conns=smbinterface.conns, newactions=newactions, maxcount=maxcount,
                           newactionsallusers=newactionsallusers, maxcountallusers=maxcountallusers,
                           uploadvols=uploadvols, maxuploadvol=maxuploadvol, plugins=plugins)


@main.route('/editor/<sampleid>', methods=['GET', 'POST'])
@login_required
def editor(sampleid):
    sample = Sample.query.get(sampleid)
    shares = Share.query.filter_by(sample=sample).all()
    hideparentactions = True if request.args.get('hideparentactions') != None and int(request.args.get('hideparentactions')) else False

    if sample == None or (sample.owner != current_user and current_user not in [share.user for share in shares]):
        return render_template('404.html'), 404
    else:
        form = NewActionForm()
        form.description.data = ''
        form.timestamp.data = date.today()

        ##### get actions for this sample and all parent samples and order them by ordnum
        actions = []
        s = sample
        while s is not None:
            actions.extend(Action.query.filter_by(sample=s).order_by(Action.ordnum).all())
            s = s.parent
            if hideparentactions:
                break
        actions = sorted(actions, key=lambda a: a.ordnum)

        return render_template('editor.html', sample=sample, actions=actions, form=form, shares=shares,
                               hideparentactions=hideparentactions)


@main.route('/help')
@login_required
def help():
    admin = User.query.filter_by(is_admin=True).first()
    return render_template('help.html', admin=admin)


@main.route('/search', methods=['GET'])
@login_required
def search():
    keyword = request.args.get('term')
    samples = Sample.query.filter_by(owner=current_user).filter(Sample.name.ilike('%'+keyword+'%')).limit(10).all()   # max 10 items
    shares = db.session.query(Share, Sample).filter(Share.user_id == current_user.id).filter(Sample.name.ilike('%'+keyword+'%')).all() # max 10 items
    shares = [s[1] for s in shares] # shares is a list of (Share, Sample) tuples
    samples.extend(shares)
    results = [{"label": s.name, "id": s.id} for s in samples]

    if request.args.get('autocomplete') is not None:
        return jsonify(results=results)
    else:
        return render_template('searchresults.html', results=results)


@main.route('/userlist', methods=['POST'])
@login_required
def userlist():
    sample = Sample.query.filter_by(id=int(request.form.get("id"))).first()
    users = User.query.all()
    sharers = [share.user for share in sample.shares]
    sharers.append(sample.owner)

    return render_template('userlist.html', users=[user for user in users if user not in sharers])


@main.route('/sharerlist', methods=['POST'])
@login_required
def sharerlist():
    sample = Sample.query.filter_by(id=int(request.form.get("id"))).first()
    sharers = [share.user for share in sample.shares]

    return jsonify(sharers=sharers)


@main.route('/loginas', methods=['GET'])
@login_required
def login_as():
    user = User.query.filter_by(id=int(request.args.get("userid"))).first()

    # check if current user has the right to do this
    if user.heir != current_user:
        return "You do not have the permission to log in as: "+user.username

    logout_user()
    login_user(user)

    return redirect("/")


@main.route('/togglearchived', methods=['POST'])
@login_required
def togglearchived():
    sample = Sample.query.filter_by(id=int(request.form.get("id"))).first()
    if sample == None or sample.owner != current_user:
        return jsonify(code=1, error="Sample does not exist or you do not have the right to access it")
    sample.isarchived = not sample.isarchived
    db.session.commit()
    return jsonify(code=0, isarchived=sample.isarchived)


@main.route('/sharesample', methods=['POST'])
@login_required
def sharesample():
    sample = Sample.query.filter_by(id=int(request.form.get("id"))).first()
    user = User.query.filter_by(id=int(request.form.get("sharewith"))).first()
    if sample == None or sample.owner != current_user:
        return jsonify(code=1, error="Sample does not exist or you do not have the right to access it")
    share = Share(sample = sample, user = user)
    db.session.add(share)
    db.session.commit()
    return jsonify(code=0, username=user.username, userid=user.id, shareid=share.id)


@main.route('/changesampleimage', methods=['POST'])
@login_required
def changesampleimage():
    sample = Sample.query.filter_by(id=int(request.form.get("id"))).first()
    if sample == None or sample.owner != current_user:
        return jsonify(code=1, error="Sample does not exist or you do not have the right to access it")
    sample.image = request.form.get('value')
    db.session.commit()
    return ""


@main.route('/delaction/<actionid>', methods=['GET', 'POST'])
@login_required
def deleteaction(actionid):
    action = Action.query.filter_by(id=int(actionid)).first()
    if action == None or action.owner != current_user:
        return render_template('404.html'), 404
    sampleid = action.sample_id
    db.session.delete(action)
    db.session.commit()
    return redirect("/sample/" + str(sampleid))


@main.route('/delsample/<sampleid>', methods=['GET', 'POST'])
@login_required
def deletesample(sampleid):
    sample = Sample.query.filter_by(id=int(sampleid)).first()
    if sample == None or sample.owner != current_user:
        return render_template('404.html'), 404
    db.session.delete(sample)  # delete cascade automatically deletes associated actions
    db.session.commit()
    return redirect("/")


@main.route('/delshare/<shareid>', methods=['GET', 'POST'])
@login_required
def deleteshare(shareid):
    share = Share.query.filter_by(id=int(shareid)).first()

    if share is None or share.sample is None:
        return jsonify(code=1, error="Share or sample does not exist")

    if share.sample.owner != current_user and share.user != current_user:
        return jsonify(code=1, error="You do not have the right to perform this operation")

    user = share.user

    db.session.delete(share)
    db.session.commit()

    if user == current_user:      # in this case the sample does not exist anymore for this user
        return jsonify(code=2)

    return jsonify(code=0, shareid=share.id)


@main.route('/changeparent', methods=['POST'])
@login_required
def changeparent():
    sample = Sample.query.filter_by(id=int(request.form.get("id"))).first()
    if sample == None or sample.owner != current_user:
        return jsonify(code=1, error="Sample does not exist or you do not have the right to access it")

    # check if we're not trying to make the snake bite its tail
    parentid = int(request.form.get('parent'))
    if (parentid != 0):
        p = Sample.query.filter_by(id=parentid).first()
        while (p.parent_id != 0):
            if (p.parent_id == sample.id):
                return jsonify(code=1, error="Cannot move sample")
            p = p.parent

    # change parent ID and remove matrix coords
    sample.parent_id = parentid
    sample.mx = None
    sample.my = None
    db.session.commit()
    return jsonify(code=0)


@main.route('/newsample', methods=['GET', 'POST'])
@login_required
def newsample():
    form = NewSampleForm()
    form.parent.choices = [(0, "/")] + [(sample.id, sample.name) for sample in Sample.query.filter(Sample.owner == current_user).order_by('name')]
    if form.validate_on_submit():
        if Sample.query.filter_by(owner=current_user, name=form.name.data).all():
            flash("You already have a sample with this name: "+form.name.data+". Please choose a different name.")
            return render_template('newsample.html', form=form)
        sample = Sample(owner=current_user, name=form.name.data, parent_id=form.parent.data, description=form.description.data)
        db.session.add(sample)
        db.session.commit()
        return redirect("/sample/" + str(sample.id))
    return render_template('newsample.html', form=form)


@main.route('/newaction/<sampleid>', methods=['POST'])
@login_required
def newaction(sampleid):
    sample = Sample.query.filter_by(id=int(sampleid)).first()
    if sample == None or (sample.owner != current_user and not sample.is_shared_with(current_user)):
        return jsonify(code=1, error="Sample does not exist or you do not have the right to access it")

    form = NewActionForm()
    if form.validate_on_submit():
        a = Action(datecreated=date.today(), timestamp=form.timestamp.data, owner=current_user, sample_id=sampleid,
                   description=form.description.data)
        db.session.add(a)
        db.session.commit()
        a.ordnum = a.id         # add ID as order number (maybe there is a more elegant way to do this?)
        db.session.commit()
    # if form was submitted but failed validation, show again to user
    # this is very important for the case where form is not validated because the
    # CSRF token passed its time limit (typically 3600s) -> users lose everything they
    # wrote otherwise (also happens when user enters invalid date)
    elif form.is_submitted():
        return jsonify(code=1, description=form.description.data)

    return jsonify(code=0)


@main.route('/swapactionorder', methods=['POST'])
@login_required
def swapactionorder():          # TODO: sort out permissions for this (e.g. who has the right to change order?)
    action = Action.query.filter_by(id = int(request.form.get('actionid'))).first()
    swapaction = Action.query.filter_by(id = int(request.form.get('swapid'))).first()
    ordnum = action.ordnum
    action.ordnum = swapaction.ordnum
    swapaction.ordnum = ordnum
    db.session.commit()
    return ""


@main.route('/resetmatrix/<sampleid>', methods=['POST'])
@login_required
def resetmatrix(sampleid):
    sample = Sample.query.filter_by(id=int(sampleid)).first()
    sample.mwidth = None
    sample.mheight = None
    for c in sample.children:
        c.mx = None
        c.my = None

    return jsonify(code=0)


@main.route('/matrixview/<sampleid>', methods=['GET', 'POST'])
@login_required
def matrixview(sampleid):
    sample = Sample.query.filter_by(id=int(sampleid)).first()
    form = NewMatrixForm()
    if form.validate_on_submit():  # TODO: do this with AJAX
        sample.mheight = int(form.height.data)
        sample.mwidth = int(form.width.data)
        db.session.commit()
    matrix = []
    children = sample.children

    if (sample.mheight):
        for y in range(sample.mheight):
            mrow = []
            for x in range(sample.mwidth):
                element = 0
                for c in range(len(children)):
                    if children[c].mx == x and children[c].my == y:
                        element = children[c].id
                mrow.append(element)
            matrix.append(mrow)

    return render_template('matrixview.html', sample=sample, form=form, matrix=matrix)


@main.route('/childbrowser/<sampleid>')
@login_required
def childbrowser(sampleid):
    sample = Sample.query.filter_by(id=int(sampleid)).first()
    return render_template('childbrowser.html', sample=sample)


@main.route('/setmatrixcoords/<sampleid>', methods=['POST'])
@login_required
def setmatrixcoords(sampleid):
    sample = Sample.query.filter_by(id=int(sampleid)).first()

    # check if any sibling has these coords already and remove them if it's the case
    for c in sample.parent.children:
        if c.mx == int(request.form.get('mx')) and c.my == int(request.form.get('my')):
            c.mx = None
            c.my = None

    # set new coords
    sample.mx = int(request.form.get('mx'))
    sample.my = int(request.form.get('my'))
    db.session.commit()
    return ""


@main.route('/plugins/<path:path>')
@login_required
def static_file(path):
    # TODO: this looks a bit unsafe to me
    return send_file('../plugins/'+path)


def validate_sample_name(name):
    if len(name) > SAMPLE_NAME_LENGTH:
        raise Exception("Name too long.")
    if Sample.query.filter_by(owner=current_user, name=name).first() is not None:
        raise Exception("Name is already taken.")
    return name


# define supported fields
supported_targets = {
    'sample': {
        'dbobject': Sample,
        'auth': 'owner',        # TODO: implement this
        'fields': {
            'name': validate_sample_name,
            'description': str
        }
    },
    'action': {
        'dbobject': Action,
        'auth': 'owner',
        'fields': {
            'timestamp': lambda x: datetime.strptime(x, '%Y-%m-%d'),
            'description': str
        }
    }
    # TODO: should add SMBresources here, for easy modification by administrator
    # TODO: in that case should also add admin required field
    # e.g.:
    #'resource': {
    #    'dbobject': SMBResource,
    #    'auth': 'admin',
    #    'fields': {
    #        'name': str
    #    }
    #}
}


@main.route('/get/<target>/<field>/<id>', methods=['GET'])
@login_required
def getfield(target, field, id):
    if not (id and target and field and target in supported_targets):
        return jsonify(code=1)

    # redefine target to simplify
    target = supported_targets[target]

    # try to get requested item from database
    item = target['dbobject'].query.get(id)

    # check if the item is valid, if the requested field is supported and if the current user
    # has the right to read it
    if not (item and item.owner == current_user and field in target['fields']):
        return jsonify(code=1)

    # return value
    if request.args.get('plain') is not None:
        return str(getattr(item, field))
    else:
        return jsonify(code=0, value=getattr(item, field))


@main.route('/set/<target>/<field>/<id>', methods=['POST'])
@login_required
def updatefield(target, field, id):
    if not (id and target and field and target in supported_targets):
        return jsonify(code=1, value='', message='Invalid request')

    value = request.form.get('value')

    # redefine target to simplify
    target = supported_targets[target]

    # try to get requested item from database
    item = target['dbobject'].query.get(id)

    # check if the item is valid, if the requested field is supported and if the current user
    # has the right to modify it
    if not (item and item.owner == current_user and field in target['fields']):
        return jsonify(code=1, value='', message='Invalid request')

    print target['dbobject'], "id:", id, "value:", value

    # try to assign value
    try:
        # check if a modifier is to be applied
        modifier = target['fields'][field]
        if modifier is not None:
            setattr(item, field, modifier(value))
        else:
            setattr(item, field, value)
    except Exception as e:
        return jsonify(code=1, value=str(getattr(item, field)), message='Error: '+str(e))

    # commit changes to database
    db.session.commit()
    return jsonify(code=0, value=value)