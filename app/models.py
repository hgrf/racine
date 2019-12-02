from . import db
from . import login_manager
from flask.ext.login import current_user
from flask.ext.login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app as app
from sqlalchemy import event
from flask_sqlalchemy import SignallingSession
from datetime import datetime

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
    activity = db.relationship('Activity', backref='user')
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
        """ determine the user's direct shares that are not mounted anywhere in his tree
        (i.e. they are at the top level)
        """
        return [s.sample for s in self.shares
                if s.mountpoint_id == 0
                and s.sample.is_accessible_for(self, direct_only=True)]


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
    shares = db.relationship('Share', backref='sample', foreign_keys='Share.sample_id', cascade="delete")
    mountedshares = db.relationship('Share', backref='mountpoint', foreign_keys='Share.mountpoint_id')
    actions = db.relationship('Action', backref='sample', cascade="delete")
    activity = db.relationship('Activity', backref='sample')

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

    def is_accessible_for(self, user, indirect_only=False, direct_only=False):
        """ go through the owner and shares of this sample and check in the hierarchy (i.e. all parents)
        if it can be accessed by user
        
        - if indirect_only is True, only look for indirect shares, i.e. parent shares
        - if direct_only is True, only look for direct shares

        indirect sharing has priority over direct sharing in order to avoid clogging up the hierarchy
        """
        
        # check for invalid flag usage
        if indirect_only and direct_only:
            raise Exception('Choose either indirect_only or direct_only or neither')

        # if looking for shared access, check first if user owns the sample
        if (indirect_only or direct_only) and self.owner == user:
            return False

        if direct_only:
            return user in [s.user for s in self.shares] and not self.is_accessible_for(user, indirect_only=True)

        parent = self.parent if indirect_only else self
        shares = []
        while parent:
            shares.append(parent.owner)
            shares.extend([s.user for s in parent.shares])
            parent = parent.parent
        return user in shares

    @property
    def mountedsamples(self):
        """ make a list of samples that are mounted in this one but exclude samples that are indirectly shared with the
        current user and samples that belong to the current user
        """

        return [s.sample for s in self.mountedshares if s.sample.is_accessible_for(current_user, direct_only=True)]
    
    @property
    def logical_parent(self):
        # determine the sample's logical parent in the current user's tree (i.e. the parent or the mountpoint)

        # first find out if the sample belongs to the current user (in this case just return the real parent)
        if self.owner == current_user:
            return self.parent
        
        # if the sample is indirectly shared with the current user, also return the real parent
        if self.is_accessible_for(current_user, indirect_only=True):
            return self.parent
        
        # if the sample is directly shared with the current user, return the mount point
        if self.is_accessible_for(current_user, direct_only=True):
            share = Share.query.filter_by(sample=self, user=current_user).first()
            return share.mountpoint


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


class Activity(db.Model):
    __tablename__ = 'activity'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    sample_id = db.Column(db.Integer, db.ForeignKey('samples.id'))
    type_id = db.Column(db.Integer, db.ForeignKey('activitytypes.id'))
    description = db.Column(db.UnicodeText)

    def __repr__(self):
        return '<Activity %r>' % self.id


# Since the activity table will probably contain a lot of entries, the activity
# type, e.g. "update:sample:description" should be encoded as an integer ID
# referring to this table. When the database models are amended, the supported
# activity types will be adapted automatically in app/__init__.py based on the
# supported_targets dictionary in app/main/views.py.
class ActivityType(db.Model):
    __tablename__ = 'activitytypes'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(256))

    activity = db.relationship('Activity', backref='type')

    def __repr__(self):
        return '<ActivityType %r>' % self.description


def record_activity(type, user=None, sample=None, description=None, commit=False):
    atype = ActivityType.query.filter_by(description=type).first()
    if atype is None:
        raise Exception('Unknown activity type: '+type)
    activity = Activity(timestamp=datetime.now(),
                        user_id=user.id if user is not None else 0,
                        sample_id=sample.id if sample is not None else 0,
                        type_id=atype.id,
                        description=description)
    db.session.add(activity)
    if commit:
        db.session.commit()
