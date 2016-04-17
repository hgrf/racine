from . import db
from . import login_manager
from flask.ext.login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

SAMPLE_NAME_LENGTH = 64


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean())
    samples = db.relationship('Sample', backref='owner')
    actions = db.relationship('Action', backref='owner')
    shares = db.relationship('Share', backref='user')
    uploads = db.relationship('Upload', backref='user')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


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
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(SAMPLE_NAME_LENGTH), unique=True, index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('samples.id'))
    sampletype_id = db.Column(db.Integer, db.ForeignKey('sampletypes.id'))
    image = db.Column(db.String(300))  # <----------- a changer
    description = db.Column(db.UnicodeText)
    isarchived = db.Column(db.Boolean)

    mwidth = db.Column(db.Integer)  # matrix width (for children)
    mheight = db.Column(db.Integer)  # matrix height (for children)
    mx = db.Column(db.Integer)  # matrix x position (for parent)
    my = db.Column(db.Integer)  # matrix y position (for parent)

    children = db.relationship('Sample', backref=db.backref('parent', remote_side=[id]))
    shares = db.relationship('Share', backref='sample')
    actions = db.relationship('Action', backref='sample', cascade="delete")

    def __repr__(self):
        return '<Sample %r>' % self.name

    def is_shared_with(self, user):
        return user in [share.user for share in self.shares]


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
    ordnum = db.Column(db.Integer)      # used to manipulate order of actions without modifying IDs
    datecreated = db.Column(db.Date)    # used to keep track of when actions are created (user cannot modify this)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    timestamp = db.Column(db.Date)
    sample_id = db.Column(db.Integer, db.ForeignKey('samples.id'))
    actiontype_id = db.Column(db.Integer, db.ForeignKey('actiontypes.id'))
    description = db.Column(db.UnicodeText)

    def __repr__(self):
        return '<Action %r>' % self.id


class SMBResource(db.Model):
    __tablename__ = 'smbresources'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    servername = db.Column(db.String(64))
    serveraddr = db.Column(db.String(64))
    sharename = db.Column(db.String(64))
    path = db.Column(db.String(256))
    userid = db.Column(db.String(64))
    password = db.Column(db.String(64))

    def __repr__(self):
        return '<SMBResource %r>' % self.id

class Share(db.Model):
    __tablename__ = 'shares'
    id = db.Column(db.Integer, primary_key=True)
    sample_id = db.Column(db.Integer, db.ForeignKey('samples.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return '<Share %r>' % self.id

class Upload(db.Model):
    __tablename__ = 'uploads'
    id = db.Column(db.Integer, primary_key=True)
    ext = db.Column(db.String(10))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    source = db.Column(db.String(256))

    def __repr__(self):
        return '<Upload %r>' % self.id