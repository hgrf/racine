from . import db
from . import login_manager
from flask.ext.login import current_user
from flask.ext.login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app as app


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
    heir_id = db.Column(db.Integer, db.ForeignKey('users.id'))      # ID of the user who inherits this users data

    inheritance = db.relationship('User', backref=db.backref('heir', remote_side=[id])) # Users who gave their data to this one

    def __repr__(self):
        return '<User %r>' % self.username

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_reset_token(self, expiration=3600):
        s = Serializer(app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id}).decode('utf-8')

    @staticmethod
    def reset_password(token, new_password):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        user = User.query.get(data.get('reset'))
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        return True


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Sample(db.Model):
    __tablename__ = 'samples'
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(SAMPLE_NAME_LENGTH))
    parent_id = db.Column(db.Integer, db.ForeignKey('samples.id'))
    image = db.Column(db.String(300))  # <----------- a changer
    description = db.Column(db.UnicodeText)
    isarchived = db.Column(db.Boolean)

    mwidth = db.Column(db.Integer)  # matrix width (for children)
    mheight = db.Column(db.Integer)  # matrix height (for children)
    mx = db.Column(db.Integer)  # matrix x position (for parent)
    my = db.Column(db.Integer)  # matrix y position (for parent)

    children = db.relationship('Sample', backref=db.backref('parent', remote_side=[id]))
    shares = db.relationship('Share', backref='sample', cascade="delete")
    actions = db.relationship('Action', backref='sample', cascade="delete")

    def __setattr__(self, name, value):
        if name == 'name':
            if value != self.name and self.query.filter_by(owner=current_user, parent_id=self.parent_id, name=value).all():
                raise Exception('You already have a sample with this name on this hierarchy level.')
        if name == 'parent_id':
            if value != self.parent_id and self.name is not None and self.query.filter_by(owner=current_user, parent_id=value, name=self.name).all():
                raise Exception('You already have a sample with this name on this hierarchy level.')
        super(Sample, self).__setattr__(name, value)

    def __repr__(self):
        return '<Sample %r>' % self.name

    def is_shared_with(self, user):
        # this means the user has write-access to this sample
        # TODO: rename this function to something more adequate, like, is_accessible()
        # go through the owner and shares of this sample and check in the hierarchy (i.e. all parents)
        # if it can be accessed by user
        parent = self
        shares = []
        while parent:
            shares.append(parent.owner)
            shares.extend([s.user for s in parent.shares])
            parent = parent.parent
        return user in shares

    def is_visible_to(self, user):
        # this means the user only has read-access to this sample
        parent = self
        while parent:
            if not parent.owner_id: # global share
                return True
            parent = parent.parent
        return self.is_shared_with(user)

class Action(db.Model):
    __tablename__ = 'actions'
    id = db.Column(db.Integer, primary_key=True)
    ordnum = db.Column(db.Integer)      # used to manipulate order of actions without modifying IDs
    datecreated = db.Column(db.Date)    # used to keep track of when actions are created (user cannot modify this)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    timestamp = db.Column(db.Date)
    sample_id = db.Column(db.Integer, db.ForeignKey('samples.id'))
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
    size = db.Column(db.Integer)
    hash = db.Column(db.String(64))

    def __repr__(self):
        return '<Upload %r>' % self.id