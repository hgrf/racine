from . import db
from . import login_manager
from flask.ext.login import current_user
from flask.ext.login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app as app
from sqlalchemy import event
from flask_sqlalchemy import SignallingSession

SAMPLE_NAME_LENGTH = 64

# https://stackoverflow.com/questions/13693872/can-sqlalchemy-events-be-used-to-update-a-denormalized-data-cache/13765857#13765857
# https://github.com/pallets/flask-sqlalchemy/issues/182
def after_flush(session, flush_context):
    """ check for any deleted shares (they are also automatically deleted if the associated sample is deleted)
        and move children or mounted samples that belong to the corresponding share user to his root
        CAREFUL: this has to be done after the flush, because if a parent sample / mountpoint is deleted,
        the database automatically sets the corresponding foreign keys to NULL
    """
    for obj in session.deleted:
        if isinstance(obj, Share):
            print "Detected share deletion: ", obj

            share = obj

            def reset_mountpoints(sample):
                # check if sample is a mountpoint for the user whose share we remove and deactivate this mountpoint
                mountedsamples = Share.query.filter_by(user=share.user, mountpoint=sample).all()
                for s in mountedsamples:
                    session.execute(Share.__table__.update().values(mountpoint_id=0).where(Share.id == s.id))
                for c in sample.children+sample.mountedsamples:
                    reset_mountpoints(c)

            def find_orphans(sample):
                for c in sample.children+sample.mountedsamples:
                    # check if sample belongs to the user whose share we remove and move it back to his tree
                    if c.owner == share.user:
                        session.execute(Sample.__table__.update().values(parent_id=0).where(Sample.id == c.id))
                    find_orphans(c)
            
            reset_mountpoints(share.sample)
            find_orphans(share.sample)
    
event.listen(SignallingSession, 'after_flush', after_flush)


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

    @property
    def directshares(self):
        return [s.sample for s in self.shares if s.mountpoint_id == 0 and not s.sample.is_shared_with(self, indirect_only=True)]


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
    shares = db.relationship('Share', backref='sample', foreign_keys = 'Share.sample_id', cascade="delete")
    mountedshares = db.relationship('Share', backref = 'mountpoint', foreign_keys = 'Share.mountpoint_id')
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

    def is_shared_with(self, user, indirect_only=False):
        # TODO: rename this function to something more adequate, like, is_accessible()
        # go through the owner and shares of this sample and check in the hierarchy (i.e. all parents)
        # if it can be accessed by user
        # if indirect_only is True, only look for indirect shares, i.e. parent shares
        parent = self.parent if indirect_only else self
        shares = []
        while parent:
            shares.append(parent.owner)
            shares.extend([s.user for s in parent.shares])
            parent = parent.parent
        return user in shares

    @property
    def mountedsamples(self):
        # TODO: current_user should actually somehow be passed as an argument to this function in order to keep it general
        # make a list of samples that are mounted in this one but exclude samples
        # that are indirectly shared with the current user and samples that belong
        # to the current user
        return [s.sample for s in self.mountedshares
                if not s.sample.is_shared_with(current_user, indirect_only=True)   # make sure that the sample is not indirectly shared
                and s.sample.is_shared_with(current_user)                          # make sure that the user has access to the sample
                and not s.sample.owner == current_user]                            # make sure that the sample does not belong to the user
        # TODO: these three lines should be cut down to a function is_shared_with(current_user, direct_only=True)


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
    mountpoint_id = db.Column(db.Integer, db.ForeignKey('samples.id'))

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
