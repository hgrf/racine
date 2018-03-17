from flask import render_template, redirect, request, jsonify, send_file, flash
from flask.ext.login import current_user, login_required, login_user, logout_user
from .. import db
from .. import plugins
from ..models import Sample, Action, User, Share, Upload
from . import main
from forms import NewSampleForm, NewActionForm, NewMatrixForm
from datetime import date, datetime, timedelta
from .. import smbinterface
from ..validators import ValidSampleName
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
    if not sampleid:
        return render_template('main.html', sample=None)
    sample = Sample.query.get(sampleid)
    if sample == None or (sample.owner != current_user and not sample.is_shared_with(current_user)):
        return render_template('404.html'), 404
    return render_template('main.html', sample=sample)


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

def recursive_add_timestamp(samples):
    print samples
    for s in samples:
        actions = sorted(s.actions, key=lambda a: a.timestamp if a.timestamp else date.today())
        s.last_action_date = actions[-1].timestamp if actions != [] and actions[-1].timestamp is not None else date.today()
        recursive_add_timestamp(s.children)

@main.route('/navbar', methods=['GET'])
@login_required
def navbar():
    inheritance = User.query.filter_by(heir=current_user).all()
    showarchived = True if request.args.get('showarchived') is not None and request.args.get('showarchived') == 'true'\
              else False
    order = request.args.get('order') if request.args.get('order') else 'id'

    # only query root level samples, the template will build the hierarchy
    samples = Sample.query.filter_by(owner=current_user, parent_id=0).all()
    shares = [s.sample for s in current_user.shares]

    # add timestamps for sorting
    if order == 'last_action_date':
        recursive_add_timestamp(samples)
        recursive_add_timestamp(shares)

    return render_template('navbar.html', samples=samples, shares=shares, inheritance=inheritance,
                           showarchived=showarchived, order=order)



@main.route('/editor/<sampleid>', methods=['GET', 'POST'])
@login_required
def editor(sampleid):
    sample = Sample.query.get(sampleid)
    shares = sample.shares
    showparentactions = True if request.args.get('showparentactions') != None and int(request.args.get('showparentactions')) else False

    if sample == None or (sample.owner != current_user and not sample.is_shared_with(current_user)):
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
            if not showparentactions:
                break
        actions = sorted(actions, key=lambda a: a.ordnum)

        return render_template('editor.html', sample=sample, actions=actions, form=form, shares=shares,
                               showparentactions=showparentactions)


@main.route('/help')
@login_required
def help():
    admin = User.query.filter_by(is_admin=True).first()
    return render_template('help.html', admin=admin)


@main.route('/search', methods=['GET'])
@login_required
def search():
    keyword = request.args.get('term').lower()
    # In order to reach really ALL samples that are accessible by the current user, we need to go through the hierarchy.
    # The most tricky samples to catch are the children of a sample that the user shares with someone else and that are
    # not explicitly shared with the user.
    #
    # The problem with the following strategy is that samples on the same hierarchy level are not given the same
    # priority in the results list. Instead the first "tree" will be given highest priority.
    def find_in(samples, keyword, limit):
        if not samples or limit < 1:
            return []
        result = []
        for s in samples:
            if keyword in s.name.lower():
                result.append(s)
            result.extend(find_in(s.children, keyword, limit-len(result)))
        return result

    own_samples = Sample.query.filter_by(owner=current_user, parent_id=0).all()
    shares = [s.sample for s in current_user.shares]
    results = [{"label": s.name, "id": s.id,
                "ownername": s.owner.username,
                "plabel": s.parent.name if s.parent_id else ''}
               for s in find_in(own_samples+shares, keyword, 10)]

    if request.args.get('autocomplete') is not None:
        return jsonify(results=results)
    else:
        return render_template('searchresults.html', results=results)


@main.route('/userlist', methods=['POST'])
@login_required
def userlist():
    sample = Sample.query.get(int(request.form.get("id")))
    users = User.query.all()
    sharers = [share.user for share in sample.shares]
    sharers.append(sample.owner)

    return render_template('userlist.html', users=[user for user in users if user not in sharers])


@main.route('/loginas', methods=['GET'])
@login_required
def login_as():
    user = User.query.get(int(request.args.get("userid")))

    # check if current user has the right to do this
    if user.heir != current_user:
        return "You do not have the permission to log in as: "+user.username

    logout_user()
    login_user(user)

    return redirect("/")


@main.route('/togglearchived', methods=['POST'])
@login_required
def togglearchived():
    sample = Sample.query.get(int(request.form.get("id")))
    if sample == None or sample.owner != current_user:
        return jsonify(code=1, error="Sample does not exist or you do not have the right to access it")
    sample.isarchived = not sample.isarchived
    db.session.commit()
    return jsonify(code=0, isarchived=sample.isarchived)


@main.route('/sharesample', methods=['POST'])
@login_required
def sharesample():
    sample = Sample.query.get(int(request.form.get("id")))
    user = User.query.get(int(request.form.get("sharewith")))
    if sample == None or sample.owner != current_user:
        return jsonify(code=1, error="Sample does not exist or you do not have the right to access it")
    share = Share(sample = sample, user = user)
    db.session.add(share)
    db.session.commit()
    return jsonify(code=0, username=user.username, userid=user.id, shareid=share.id)


@main.route('/delaction/<actionid>', methods=['GET', 'POST'])
@login_required
def deleteaction(actionid):
    action = Action.query.get(int(actionid))
    if action == None or action.owner != current_user:
        return render_template('404.html'), 404
    sampleid = action.sample_id
    db.session.delete(action)
    db.session.commit()
    return redirect("/sample/" + str(sampleid))


@main.route('/delsample/<sampleid>', methods=['GET', 'POST'])
@login_required
def deletesample(sampleid):
    sample = Sample.query.get(int(sampleid))
    if sample == None or sample.owner != current_user:
        return render_template('404.html'), 404
    db.session.delete(sample)  # delete cascade automatically deletes associated actions
    db.session.commit()
    return redirect("/")


@main.route('/delshare/<shareid>', methods=['GET', 'POST'])
@login_required
def deleteshare(shareid):
    share = Share.query.get(int(shareid))

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
    sample = Sample.query.get(int(request.form.get("id")))
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
    if form.validate_on_submit():
        if not Sample.query.get(form.parentid.data) and form.parentid.data:
            flash("Please select a valid parent sample or leave that field empty.")
            return render_template('newsample.html', form=form, parenterror=True)
        sample = Sample(owner=current_user, name=form.name.data,
                        parent_id=form.parentid.data if form.parentid.data else 0,
                        description=form.description.data)
        db.session.add(sample)
        db.session.commit()
        return redirect("/sample/" + str(sample.id))
    return render_template('newsample.html', form=form)


@main.route('/newaction/<sampleid>', methods=['POST'])
@login_required
def newaction(sampleid):
    sample = Sample.query.get(int(sampleid))
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
    action = Action.query.get(int(request.form.get('actionid')))
    swapaction = Action.query.get(int(request.form.get('swapid')))
    ordnum = action.ordnum
    action.ordnum = swapaction.ordnum
    swapaction.ordnum = ordnum
    db.session.commit()
    return ""


@main.route('/resetmatrix/<sampleid>', methods=['POST'])
@login_required
def resetmatrix(sampleid):
    sample = Sample.query.get(int(sampleid))
    sample.mwidth = None
    sample.mheight = None
    for c in sample.children:
        c.mx = None
        c.my = None

    return jsonify(code=0)


@main.route('/matrixview/<sampleid>', methods=['GET', 'POST'])
@login_required
def matrixview(sampleid):
    sample = Sample.query.get(int(sampleid))
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
    sample = Sample.query.get(int(sampleid))
    return render_template('childbrowser.html', sample=sample)


@main.route('/setmatrixcoords/<sampleid>', methods=['POST'])
@login_required
def setmatrixcoords(sampleid):
    sample = Sample.query.get(int(sampleid))

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


# define supported fields
supported_targets = {
    'sample': {
        'dbobject': Sample,
        'auth': 'owner',        # TODO: implement this
        'fields': {
            'name': ValidSampleName.validate,
            'description': str,
            'image': str
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