from flask import render_template, redirect, request, jsonify, send_file, flash
from flask.ext.login import current_user, login_required, login_user, logout_user
from .. import db
from .. import plugins
from ..models import Sample, Action, User, Share, Upload, SMBResource
from . import main
from forms import NewSampleForm, NewActionForm, NewMatrixForm
from datetime import date, datetime, timedelta
from .. import smbinterface
from ..validators import ValidSampleName
from sqlalchemy.sql import func
from sqlalchemy import not_
import os


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
    if sample is None or not sample.is_accessible_for(current_user):
        return render_template('404.html'), 404
    return render_template('main.html', sample=sample)


@main.route('/welcome')
@login_required
def welcome():
    # get free disk space
    statvfs = os.statvfs(os.path.dirname(__file__))
    availablevol = statvfs.f_frsize*statvfs.f_bavail

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
    totuploadvol = 0
    for u in uploadvols:
        maxuploadvol = max(maxuploadvol, u[1])
        totuploadvol += u[1] if u[1] is not None else 0

    # get user activity only for current user (every user will see this for his samples)
    stmt = db.session.query(Action.sample_id, func.count('*').label('action_count')).filter(Action.owner_id == current_user.id).filter(Action.datecreated > aweekago).group_by(Action.sample_id).subquery()
    newactions = db.session.query(Sample, stmt.c.action_count).outerjoin(stmt, Sample.id == stmt.c.sample_id).order_by(Sample.id).all()
    maxcount = 0
    for n in newactions: maxcount = max(maxcount, n[1])

    return render_template('welcome.html', conns=smbinterface.conns, newactions=newactions, maxcount=maxcount,
                           newactionsallusers=newactionsallusers, maxcountallusers=maxcountallusers,
                           uploadvols=uploadvols, maxuploadvol=maxuploadvol, plugins=plugins,
                           totuploadvol=totuploadvol, availablevol=availablevol)


def recursive_add_timestamp(samples):
    for s in samples:
        actions = sorted(s.actions, key=lambda a: a.timestamp if a.timestamp else date.today())
        s.last_action_date = actions[-1].timestamp if actions != [] and actions[-1].timestamp is not None else date.today()
        recursive_add_timestamp(s.children+s.mountedsamples)


@main.route('/navbar', methods=['GET'])
@login_required
def navbar():
    inheritance = User.query.filter_by(heir=current_user).all()
    showarchived = True if request.args.get('showarchived') is not None and request.args.get('showarchived') == 'true'\
              else False
    order = request.args.get('order') if request.args.get('order') else 'id'

    # only query root level samples, the template will build the hierarchy
    samples = Sample.query.filter_by(owner=current_user, parent_id=0).all()
    samples.extend(current_user.directshares)

    # add timestamps for sorting
    if order == 'last_action_date':
        recursive_add_timestamp(samples)

    return render_template('navbar.html', samples=samples, inheritance=inheritance,
                           showarchived=showarchived, order=order)


@main.route('/editor/<sampleid>', methods=['GET', 'POST'])
@login_required
def editor(sampleid):
    sample = Sample.query.get(sampleid)
    shares = sample.shares
    showparentactions = True if request.args.get('showparentactions') != None and int(request.args.get('showparentactions')) else False

    if sample is None or not sample.is_accessible_for(current_user):
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
    admins = User.query.filter_by(is_admin=True).all()
    return render_template('help.html', admins=admins)


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
            result.extend(find_in(s.children+s.mountedsamples, keyword, limit-len(result)))
        return result

    own_samples = Sample.query.filter_by(owner=current_user, parent_id=0).all()
    shares = current_user.directshares
    results = [{"name": s.name, "id": s.id,
                "ownername": s.owner.username,
                "mysample": (s.owner == current_user),
                "parentname": s.parent.name if s.parent_id else ''}
               for s in find_in(own_samples+shares, keyword, 10)]

    if request.args.get('autocomplete') is not None:
        return jsonify(results=results)
    else:
        return render_template('searchresults.html', results=results, term=keyword)


@main.route('/userlist', methods=['POST'])
@login_required
def userlist():
    # get list of all users
    users = User.query.all()

    # determine mode
    mode = request.form.get("mode")
    if mode == "share":
        # get list of people who already share this sample
        sample = Sample.query.get(int(request.form.get("sampleid")))
        sharers = [share.user for share in sample.shares]
        sharers.append(sample.owner)

        # get list of max. 5 people that the current user has recently shared with
        list1 = [{"id": share.id, "name": share.user.username} for share in Share.query.\
            outerjoin(Sample, Sample.id==Share.sample_id).\
            filter(Sample.owner_id == current_user.id). \
            filter(not_(Share.user_id.in_([x.id for x in sharers]))).\
            order_by(Share.id.desc()).\
            group_by(Share.user_id).\
            limit(5).\
            all()]

        # get list of max. 5 people that have recently shared with current user
        list2 = [{"id": share.id, "name": share.sample.owner.username} for share in Share.query.\
            filter(Share.user_id == current_user.id).\
            outerjoin(Sample, Sample.id==Share.sample_id).\
            filter(not_(Sample.owner_id.in_([x.id for x in sharers]))).\
            order_by(Share.id.desc()).\
            group_by(Sample.owner_id).\
            limit(5).\
            all()]

        # now combine them, order by descending ID, remove duplicates and truncate to 5 elements
        list = sorted(list1+list2, key=lambda x:x["id"], reverse=True)
        finallist = []
        for i,x in enumerate(list):
            if len(finallist) > 4:
                break
            if x["name"] not in finallist:
                finallist.append(x["name"])

        return jsonify(users=[user.username for user in users if user not in sharers], recent=finallist)
    elif mode == "leave":
        return jsonify(users=[user.username for user in users if user != current_user and user.heir is None])
    else:
        return jsonify(users=[user.username for user in users])


@main.route('/loginas', methods=['GET'])
@login_required
def login_as():
    user = User.query.get(int(request.args.get("userid")))

    # check if current user has the right to do this
    if not current_user.is_admin and user.heir != current_user:
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


@main.route('/createshare', methods=['POST'])
@login_required
def createshare():
    sample = Sample.query.get(int(request.form.get("sampleid")))
    user = None
    if request.form.get("userid"):
        user = User.query.get(int(request.form.get("userid")))
    elif request.form.get("username"):
        user = User.query.filter_by(username=(request.form.get("username"))).first()
    if user is None:
        return jsonify(code=1, error="No valid user ID or name given"), 500
    if sample is None or sample.owner != current_user:
        return jsonify(code=1, error="Sample does not exist or you do not have the right to access it"), 500
    if user in [x.user for x in sample.shares]:
        return jsonify(code=1, error="This share already exists"), 500
    share = Share(sample = sample, user = user, mountpoint_id = 0)
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
    if sample is None or not sample.is_accessible_for(current_user):
        return jsonify(code=1, error="Sample does not exist or you do not have the right to access it")

    # check if we're not trying to make the snake bite its tail
    parentid = int(request.form.get('parent'))
    if parentid != 0:
        p = Sample.query.filter_by(id=parentid).first()
        while p.logical_parent:
            if p.logical_parent == sample:
                return jsonify(code=1, error="Cannot move sample")
            p = p.logical_parent

    # check if the current user is the sample owner, otherwise get corresponding share
    if sample.owner != current_user:
        if sample.is_accessible_for(current_user, indirect_only=True):
            return jsonify(code=1, error="The sample owner ("+sample.owner.username+") has fixed the sample's location.")
  
        share = Share.query.filter_by(sample=sample, user=current_user).first()
        if share is None:
            return jsonify(code=1, error="Could not find corresponding share")
        try:
            share.mountpoint_id = parentid
            db.session.commit()
        except Exception as e:
            return jsonify(code=1, error="Exception: "+e.message)
    else:
    # change parent ID and remove matrix coords
        try:
            sample.parent_id = parentid
            sample.mx = None
            sample.my = None
            db.session.commit()
        except Exception as e:
            return jsonify(code=1, error=e.message)
    return jsonify(code=0)


@main.route('/newsample', methods=['GET', 'POST'])
@login_required
def newsample():
    form = NewSampleForm()
    if form.validate_on_submit():
        parentid = int(form.parentid.data) if form.parentid.data else 0
        if not Sample.query.get(form.parentid.data) and form.parentid.data:
            flash("Please select a valid parent sample or leave that field empty.")
            return render_template('newsample.html', form=form, parenterror=True)
        try:
            sample = Sample(owner=current_user, name=form.name.data, parent_id=parentid,
                            description=form.description.data)
            db.session.add(sample)
            db.session.commit()
            return redirect("/sample/" + str(sample.id))
        except Exception as e:
            flash(e.message)
    return render_template('newsample.html', form=form)


@main.route('/newaction/<sampleid>', methods=['POST'])
@login_required
def newaction(sampleid):
    sample = Sample.query.get(int(sampleid))
    if sample is None or not sample.is_accessible_for(current_user):
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


def str_to_bool(str):
    if str.lower() == 'true' or str == '1':
        return True
    elif str.lower() == 'false' or str == '0':
        return False
    else:
        raise Exception('String could not be converted to boolean')


# use the email validator from the new user form
# TODO: this could be generalised for any field by passing the form and the field name as parameters to this function
#       however, the approach in app/validators.py is also a solution (i.e. writing my own validators that are
#       compatible both with the below field updating and the WTForms validation
from ..settings.forms import NewUserForm
def validate_email(str):
    form = NewUserForm()
    form.email.data = str
    if form.email.validate(form):
        return str
    else:
        # raise exception with first validation error as message
        raise Exception(form.email.errors[0])


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
    },
    'smbresource': {
        'dbobject': SMBResource,
        'auth': 'admin',
        'fields': {
            'name': str,
            'servername': str,
            'serveraddr': str,
            'sharename': str,
            'path': str,
            'userid': str,
            'password': str
        }
    },
    'user': {
        'dbobject': User,
        'auth': 'admin',
        'fields': {
            'username': str,
            'email': validate_email,
            'is_admin': str_to_bool
        }
    }
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

    # check if the item is valid and if the requested field is supported
    if not (item and field in target['fields']):
        return jsonify(code=1)

    # check if the current user is authorized to access this item
    if      not (target['auth'] == 'owner' and item.owner == current_user)\
        and not (target['auth'] == 'admin' and current_user.is_admin):
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

    # check if the item is valid and if the requested field is supported
    if not (item and field in target['fields']):
        return jsonify(code=1, value='', message='Invalid request')

    # check if the current user is authorized to access this item
    if      not (target['auth'] == 'owner' and item.owner == current_user)\
        and not (target['auth'] == 'admin' and current_user.is_admin):
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