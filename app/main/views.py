from flask import render_template, redirect, request, jsonify, send_file
from .. import db
from ..models import Sample
from ..models import SampleType
from ..models import Action
from ..models import ActionType
from ..models import SMBResource
from ..models import SAMPLE_NAME_LENGTH   # <-- sort this out
from . import main
from forms import NewSampleForm, NewActionForm, NewMatrixForm
from datetime import date, datetime
from smb.SMBConnection import SMBConnection
import socket
import tempfile
import os
import io


# see http://flask.pocoo.org/snippets/67/
def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


@main.route('/')
def index():
    return render_template('editor.html', samples=Sample.query.all(), sampletypes=SampleType.query.all(),
                           actiontypes=ActionType.query.all())


@main.route('/allsamples')
def allsamples():
    return render_template('allsamples.html', samples=Sample.query.all())


@main.route('/sample/<sampleid>', methods=['GET', 'POST'])
def sampleeditor(sampleid):
    sample = Sample.query.get(sampleid)
    if sample == None:
        return render_template('404.html'), 404
    else:
        form = NewActionForm()
        form.actiontype.choices = [(actiontype.id, actiontype.name) for actiontype in ActionType.query.order_by('name')]
        form.description.data = ''
        form.timestamp.data = date.today()
        if (request.args.get("editorframe") == "true"):
            return render_template('editorframe.html', samples=Sample.query.all(), sample=sample,
                                   actions=sample.actions, form=form, sampletypes=SampleType.query.all(),
                                   actiontypes=ActionType.query.all())
        else:
            return render_template('editor.html', samples=Sample.query.all(), sample=sample, actions=sample.actions,
                                   form=form, sampletypes=SampleType.query.all(), actiontypes=ActionType.query.all())


@main.route('/changesamplename', methods=['POST'])
def changesamplename():
    sample = Sample.query.filter_by(id=int(request.form.get("id"))).first()
    newname = request.form.get('value')
    if len(newname) > SAMPLE_NAME_LENGTH:
        return jsonify(code=1, error="Name too long", name=sample.name)
    if (Sample.query.filter_by(name=newname).first() == None):
        sample.name = newname
        db.session.commit()
        return jsonify(code=0, name=newname, id=sample.id)
    else:
        return jsonify(code=1, error="Name is already taken", name=sample.name)


@main.route('/changesampletype', methods=['POST'])
def changesampletype():
    sample = Sample.query.filter_by(id=int(request.form.get("id"))).first()
    sample.sampletype_id = int(request.form.get('value'))
    db.session.commit()
    return sample.sampletype.name


@main.route('/changesampleimage', methods=['POST'])
def changesampleimage():
    sample = Sample.query.filter_by(id=int(request.form.get("id"))).first()
    sample.image = request.form.get('value')
    db.session.commit()
    return ""


@main.route('/changeactiondate', methods=['POST'])
def changeactiondate():
    action = Action.query.filter_by(id=int(request.form.get("id"))).first()
    try:
        action.timestamp = datetime.strptime(request.form.get('value'), '%Y-%m-%d')
    except ValueError:
        return jsonify(code=1, error="Not a valid date", id=action.id, date=action.timestamp.strftime('%Y-%m-%d'))
    db.session.commit()
    return jsonify(code=0, id=action.id, date=action.timestamp.strftime('%Y-%m-%d'))


@main.route('/changeactiontype', methods=['POST'])
def changeactiontype():
    action = Action.query.filter_by(id=int(request.form.get("id"))).first()
    action.actiontype_id = request.form.get('value')
    db.session.commit()
    return action.actiontype.name


@main.route('/changeactiondesc', methods=['POST'])
def changeactiondesc():
    action = Action.query.filter_by(id=int(request.form.get("id"))).first()
    action.description = request.form.get('value')
    db.session.commit()
    return action.description


@main.route('/delaction/<actionid>', methods=['GET', 'POST'])
def deleteaction(actionid):
    action = Action.query.filter_by(id=int(actionid)).first()
    sampleid = action.sample_id
    db.session.delete(action)
    db.session.commit()
    return redirect("/sample/" + str(sampleid))


@main.route('/delsample/<sampleid>', methods=['GET', 'POST'])
def deletesample(sampleid):
    sample = Sample.query.filter_by(id=int(sampleid)).first()
    db.session.delete(sample)  # delete cascade automatically deletes associated actions
    db.session.commit()
    return redirect("/")


@main.route('/changeparent', methods=['POST'])
def changeparent():
    sample = Sample.query.filter_by(id=int(request.form.get("id"))).first()

    # check if we're not trying to make the snake bite its tail
    parentid = int(request.form.get('parent'))
    if (parentid != 0):
        p = Sample.query.filter_by(id=parentid).first()
        while (p.parent_id != 0):
            if (p.parent_id == sample.id):
                return "Can't move item"
            p = p.parent

    sample.parent_id = parentid
    db.session.commit()
    return ""


@main.route('/newsample', methods=['GET', 'POST'])
def newsample():
    form = NewSampleForm()
    form.sampletype.choices = [(sampletype.id, sampletype.name) for sampletype in SampleType.query.order_by('name')]
    form.parent.choices = [(0, "/")] + [(sample.id, sample.name) for sample in Sample.query.order_by('name')]
    if form.validate_on_submit():
        sample = Sample(name=form.name.data, sampletype_id=form.sampletype.data, parent_id=form.parent.data)
        db.session.add(sample)
        db.session.commit()
        return redirect("/sample/" + str(sample.id))
    return render_template('newsample.html', form=form)


@main.route('/newaction/<sampleid>', methods=['POST'])
def newaction(sampleid):
    form = NewActionForm()
    form.actiontype.choices = [(actiontype.id, actiontype.name) for actiontype in ActionType.query.order_by('name')]
    if form.validate_on_submit():  # what about CSRF protection?? (see http://flask-wtf.readthedocs.org/en/latest/csrf.html)
        print form.timestamp.data
        print form.actiontype.data
        print form.description.data
        db.session.add(Action(timestamp=form.timestamp.data, sample_id=sampleid, actiontype_id=form.actiontype.data,
                              description=form.description.data))
        db.session.commit()
    return ""


######################### Image browser
class FileTile:
    name = ""
    ext = ""
    image = ""


@main.route('/browser', defaults={'address': ''})
@main.route('/browser/<path:address>')
def browser(address):
    # for the moment we'll only use the first database entry
    # TODO: add possibility to choose from SMBResources
    resource = SMBResource.query.filter_by(id=1).first()
    client_machine_name = "SampleManagerWeb"
    server_ip = socket.gethostbyname(resource.serveraddr)
    image_extensions = [".jpg", ".jpeg", ".png"]
    # need to convert unicode -> string apparently... (checked with print type(resource.servername))
    conn = SMBConnection(str(resource.userid), str(resource.password), client_machine_name, str(resource.servername),
                         use_ntlm_v2=True)
    assert conn.connect(server_ip, 139)

    files = []
    folders = []
    for i in conn.listPath(resource.sharename, address):
        f = FileTile()
        f.name, f.ext = os.path.splitext(i.filename)
        if not i.isDirectory:
            if f.ext.lower() in image_extensions:
                f.image = "/browser/img/" + address + (
                    "" if address == "" else "/") + f.name + f.ext  # will at some point cause problems with big image files, consider caching compressed icons
            else:
                f.image = "/static/file.png"
            files.append(f)
        else:
            f.image = "/static/folder.png"
            folders.append(f)

    files = sorted(files, key=lambda f: f.name)
    folders = sorted(folders, key=lambda f: f.name)
    return render_template('browserframe.html', files=files, folders=folders, address=address)


@main.route('/browser/img/<path:image>')
def browserimage(image):
    # for the moment we'll only use the first database entry
    # TODO: add possibility to choose from SMBResources
    resource = SMBResource.query.filter_by(id=1).first()
    client_machine_name = "SampleManagerWeb"
    server_ip = socket.gethostbyname(resource.serveraddr)
    image_extensions = [".jpg", ".jpeg", ".png"]
    # need to convert unicode -> string apparently... (checked with print type(resource.servername))
    conn = SMBConnection(str(resource.userid), str(resource.password), client_machine_name, str(resource.servername),
                         use_ntlm_v2=True)
    assert conn.connect(server_ip, 139)

    file_obj = tempfile.NamedTemporaryFile()
    file_attributes, filesize = conn.retrieveFile(resource.sharename, image, file_obj)

    file_obj.seek(0)
    image_binary = file_obj.read()

    file_obj.close()

    return send_file(io.BytesIO(image_binary))


@main.route('/matrixview/<sampleid>', methods=['GET', 'POST'])
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
def childbrowser(sampleid):
    sample = Sample.query.filter_by(id=int(sampleid)).first()
    return render_template('childbrowser.html', sample=sample)


@main.route('/setmatrixcoords/<sampleid>', methods=['POST'])
def setmatrixcoords(sampleid):
    sample = Sample.query.filter_by(id=int(sampleid)).first()
    sample.mx = int(request.form.get('mx'))
    sample.my = int(request.form.get('my'))
    db.session.commit()
    return ""