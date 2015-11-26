import os
from flask import Flask, render_template, redirect, request, flash, jsonify, send_file
from flask.ext.bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.wtf import Form
from flask.ext import wtf
from wtforms import SelectField, SubmitField, TextAreaField, StringField
from wtforms.widgets import TextArea
from wtforms.fields.html5 import DateField
from datetime import date, datetime
import io

import tempfile
from smb.SMBConnection import SMBConnection

SAMPLE_NAME_LENGTH = 64

app = Flask(__name__)
bootstrap = Bootstrap(app)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database/data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
db = SQLAlchemy(app)

app.config['SECRET_KEY'] = 'hard to guess string'


##################### Database Model
class SampleType(db.Model):
  __tablename__ = 'sampletypes'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(64), unique=True)
  samples = db.relationship('Sample', backref='sampletype')

  def __repr__(self):
    return '<SampleType %r>' % self.name

class Sample(db.Model):
  __tablename__ = 'samples'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(SAMPLE_NAME_LENGTH), unique=True, index=True)
  parent_id = db.Column(db.Integer, db.ForeignKey('samples.id'))
  sampletype_id = db.Column(db.Integer, db.ForeignKey('sampletypes.id'))
  image = db.Column(db.String(300))   # <----------- a changer

  mwidth = db.Column(db.Integer)      # matrix width (for children)
  mheight = db.Column(db.Integer)     # matrix height (for children)
  mx = db.Column(db.Integer)          # matrix x position (for parent)
  my = db.Column(db.Integer)          # matrix y position (for parent)

  children = db.relationship('Sample', backref=db.backref('parent', remote_side=[id]))
  actions = db.relationship('Action', backref='sample', cascade="delete")

  def __repr__(self):
    return '<Sample %r>' % self.name

class ActionType(db.Model):
  __tablename__ = 'actiontypes'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(64), unique=True)
  actions = db.relationship('Action', backref='actiontype')

  def __repr__(self):
    return '<ActionType %r>' % self.name

class Action(db.Model):
  __tablename__ = 'actions'
  id = db.Column(db.Integer, primary_key=True)
  timestamp = db.Column(db.Date)
  sample_id = db.Column(db.Integer, db.ForeignKey('samples.id'))
  actiontype_id = db.Column(db.Integer, db.ForeignKey('actiontypes.id'))
  description = db.Column(db.UnicodeText)

  def __repr__(self):
    return '<Action %r>' % self.id


####################### Forms
class NewActionForm(Form):
  timestamp = DateField('Date:')
  actiontype = SelectField('Action type:', coerce=int)
  description = TextAreaField('Description:')
  submit = SubmitField('Submit')

class NewSampleForm(Form):
  name = StringField('Sample name:')
  parent = SelectField('Parent:', coerce=int)
  sampletype = SelectField('Sample type:', coerce=int)
  submit = SubmitField('Submit')

class NewTypeForm(Form):
  name = StringField('Type name:')
  submit = SubmitField('Submit')

class NewMatrixForm(Form):
  height = StringField('Height:')   # use some sort of integer field here!
  width = StringField('Width:')     # use some sort of integer field here!
  submit = SubmitField('Submit')

# see http://flask.pocoo.org/snippets/67/
def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

#################### Error Handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/allsamples')
def allsamples():
  return render_template('allsamples.html', samples=Sample.query.all())


######################## Sample Editor ##################################
@app.route('/')
def index():
  return render_template('editor.html', samples=Sample.query.all(), sampletypes=SampleType.query.all(), actiontypes=ActionType.query.all())

@app.route('/sample/<sampleid>', methods=['GET', 'POST'])
def sampleeditor(sampleid):
  sample = Sample.query.get(sampleid)
  if sample == None:
    return render_template('404.html'), 404
  else:
    form = NewActionForm()
    form.actiontype.choices=[(actiontype.id, actiontype.name) for actiontype in ActionType.query.order_by('name')]
    form.description.data = ''
    form.timestamp.data = date.today()
    if(request.args.get("editorframe")=="true"):
      return render_template('editorframe.html', samples=Sample.query.all(), sample=sample, actions=sample.actions, form=form, sampletypes=SampleType.query.all(), actiontypes=ActionType.query.all())
    else:
      return render_template('editor.html', samples=Sample.query.all(), sample=sample, actions=sample.actions, form=form, sampletypes=SampleType.query.all(), actiontypes=ActionType.query.all())

@app.route('/newaction/<sampleid>', methods=['POST'])
def newaction(sampleid):
  form = NewActionForm()
  form.actiontype.choices=[(actiontype.id, actiontype.name) for actiontype in ActionType.query.order_by('name')]
  if form.validate_on_submit():       # what about CSRF protection?? (see http://flask-wtf.readthedocs.org/en/latest/csrf.html)
    print form.timestamp.data
    print form.actiontype.data
    print form.description.data
    db.session.add(Action(timestamp=form.timestamp.data, sample_id=sampleid, actiontype_id=form.actiontype.data, description=form.description.data))
    db.session.commit()
  return ""

@app.route('/changeparent', methods=['POST'])
def changeparent():
  sample = Sample.query.filter_by(id=int(request.form.get("id"))).first()

  # check if we're not trying to make the snake bite its tail
  parentid = int(request.form.get('parent'))
  if(parentid != 0):
    p = Sample.query.filter_by(id=parentid).first()
    while(p.parent_id != 0):
      if(p.parent_id == sample.id):
        return "Can't move item"
      p = p.parent

  sample.parent_id = parentid
  db.session.commit()
  return ""

@app.route('/changesamplename', methods=['POST'])
def changesamplename():
  sample = Sample.query.filter_by(id=int(request.form.get("id"))).first()
  newname = request.form.get('value')
  if len(newname) > SAMPLE_NAME_LENGTH:
    return jsonify(code=1, error="Name too long", name=sample.name)
  if(Sample.query.filter_by(name=newname).first() == None):
    sample.name = newname
    db.session.commit()
    return jsonify(code=0, name=newname, id=sample.id)
  else:
    return jsonify(code=1, error="Name is already taken", name=sample.name)

@app.route('/changesampletype', methods=['POST'])
def changesampletype():
  sample = Sample.query.filter_by(id=int(request.form.get("id"))).first()
  sample.sampletype_id = int(request.form.get('value'))
  db.session.commit()
  return sample.sampletype.name

@app.route('/changesampleimage', methods=['POST'])
def changesampleimage():
  sample = Sample.query.filter_by(id=int(request.form.get("id"))).first()
  sample.image = request.form.get('value')
  db.session.commit()
  return ""

@app.route('/changeactiondate', methods=['POST'])
def changeactiondate():
  action = Action.query.filter_by(id=int(request.form.get("id"))).first()
  try:
    action.timestamp = datetime.strptime(request.form.get('value'), '%Y-%m-%d')
  except ValueError:
    return jsonify(code=1, error="Not a valid date", id=action.id, date=action.timestamp.strftime('%Y-%m-%d'))
  db.session.commit()
  return jsonify(code=0, id=action.id, date=action.timestamp.strftime('%Y-%m-%d'))

@app.route('/changeactiontype', methods=['POST'])
def changeactiontype():
  action = Action.query.filter_by(id=int(request.form.get("id"))).first()
  action.actiontype_id = request.form.get('value')
  db.session.commit()
  return action.actiontype.name

@app.route('/changeactiondesc', methods=['POST'])
def changeactiondesc():
  action = Action.query.filter_by(id=int(request.form.get("id"))).first()
  action.description = request.form.get('value')
  db.session.commit()
  return action.description

@app.route('/delaction/<actionid>', methods=['GET', 'POST'])
def deleteaction(actionid):
  action = Action.query.filter_by(id=int(actionid)).first()
  sampleid = action.sample_id
  db.session.delete(action)
  db.session.commit()
  return redirect("/sample/"+str(sampleid))

@app.route('/delsample/<sampleid>', methods=['GET', 'POST'])
def deletesample(sampleid):
  sample = Sample.query.filter_by(id=int(sampleid)).first()
  db.session.delete(sample) # delete cascade automatically deletes associated actions
  db.session.commit()
  return redirect("/")


@app.route('/newsample', methods=['GET', 'POST'])
def newsample():
  form = NewSampleForm()
  form.sampletype.choices=[(sampletype.id, sampletype.name) for sampletype in SampleType.query.order_by('name')]
  form.parent.choices=[(0, "/")]+[(sample.id, sample.name) for sample in Sample.query.order_by('name')]
  if form.validate_on_submit():
    sample = Sample(name=form.name.data, sampletype_id=form.sampletype.data, parent_id=form.parent.data)
    db.session.add(sample)
    db.session.commit()
    return redirect("/sample/"+str(sample.id))
  return render_template('newsample.html', form=form)

######################## Matrix view: 1st draft ##################################
@app.route('/matrixview/<sampleid>', methods=['GET', 'POST'])
def matrixview(sampleid):
  sample = Sample.query.filter_by(id=int(sampleid)).first()
  form = NewMatrixForm()
  if form.validate_on_submit():   # TODO: do this with AJAX
    sample.mheight = int(form.height.data)
    sample.mwidth = int(form.width.data)
    db.session.commit()
  matrix = []
  children = sample.children

  if(sample.mheight):
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

@app.route('/childbrowser/<sampleid>')
def childbrowser(sampleid):
  sample = Sample.query.filter_by(id=int(sampleid)).first()
  return render_template('childbrowser.html', sample=sample)

@app.route('/setmatrixcoords/<sampleid>', methods=['POST'])
def setmatrixcoords(sampleid):
  sample = Sample.query.filter_by(id=int(sampleid)).first()
  sample.mx = int(request.form.get('mx'))
  sample.my = int(request.form.get('my'))
  db.session.commit()
  return ""

######################### Image browser
class FileTile:
  name = ""
  ext = ""
  image = ""

@app.route('/browser', defaults={'address': ''})
@app.route('/browser/<path:address>')
def browser(address):
  userID = ""
  password = ""
  client_machine_name = "SampleManagerWeb"
  server_name = "blechbox"
  server_ip = "127.0.0.1"
  image_extensions = [".jpg", ".jpeg", ".png"]

  conn = SMBConnection(userID, password, client_machine_name, server_name, use_ntlm_v2 = True)
  assert conn.connect(server_ip, 139)

  files = []
  folders = []
  for i in conn.listPath('cleanroom', address):
    f = FileTile()
    f.name, f.ext = os.path.splitext(i.filename)
    if not i.isDirectory:
      if f.ext.lower() in image_extensions:
        f.image = "/browser/img/"+address+ ("" if address=="" else "/") +f.name+f.ext      # will at some point cause problems with big image files, consider caching compressed icons
      else:
        f.image = "/static/file.png"
      files.append(f)
    else:
      f.image = "/static/folder.png"
      folders.append(f)

  if(request.args.get("browserframe")=="true"):
    return render_template('browserframe.html', files=files, folders=folders, address=address)
  else:
    return render_template('browser.html', files=files, folders=folders, address=address)

@app.route('/browser/img/<path:image>')
def browserimage(image):
  print image
  userID = ""
  password = ""
  client_machine_name = "SampleManagerWeb"
  server_name = "blechbox"
  server_ip = "127.0.0.1"
  image_extensions = [".jpg", ".jpeg", ".png"]

  conn = SMBConnection(userID, password, client_machine_name, server_name, use_ntlm_v2 = True)
  assert conn.connect(server_ip, 139)

  file_obj = tempfile.NamedTemporaryFile()
  file_attributes, filesize = conn.retrieveFile('cleanroom', image, file_obj)

  file_obj.seek(0)
  image_binary = file_obj.read()

  file_obj.close()

  return send_file(io.BytesIO(image_binary))


######################### Settings
@app.route('/settings/overview')
def set_overview():
  return render_template('settings-overview.html')

@app.route('/settings/sampletypes', methods=['GET', 'POST'])
def set_sampletypes():
  form = NewTypeForm()
  if form.validate_on_submit():
    db.session.add(SampleType(name=form.name.data))
    db.session.commit()
    form.name.data = ''
  return render_template('settings-sampletypes.html', sampletypes=SampleType.query.all(), form=form)

@app.route('/settings/actiontypes', methods=['GET', 'POST'])
def set_actiontypes():
  form = NewTypeForm()
  if form.validate_on_submit():
    db.session.add(ActionType(name=form.name.data))
    db.session.commit()
    form.name.data = ''
  return render_template('settings-actiontypes.html', actiontypes=ActionType.query.all(), form=form)

class ShutdownForm(Form):
  submit = SubmitField('Confirm shutdown')

@app.route('/settings/shutdown', methods=['GET', 'POST'])
def set_shutdown():
  form=ShutdownForm()
  if form.validate_on_submit():
    shutdown_server()
    return 'Server shutting down...'
  return render_template('settings-shutdown.html', form=form)


if __name__ == '__main__':
  db.create_all()
  app.run(debug=True, host='0.0.0.0')
