import base64
import os
from datetime import timedelta

from . import db
from . import login_manager
from flask_login import current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app as app
from sqlalchemy import event
from flask_sqlalchemy import SignallingSession
from datetime import datetime

SAMPLE_NAME_LENGTH = 64


def deleted_sample_handler(session, sample):
    def recursive(sample):
        # move everything that is mounted here back to the root
        session.execute(
            Share.__table__.update().values(mountpoint_id=0).where(Share.mountpoint_id == sample.id)
        )

        # go down the hierarchy and perform the same operations
        for s in sample.children:
            recursive(s)

            if s.owner == current_user:
                # if the sample down the hierarchy belongs to the current user, also mark it as deleted
                session.execute(
                    Sample.__table__.update().values(isdeleted=True).where(Sample.id == s.id)
                )
                # delete all corresponding news
                for news in session.execute(News.__table__.select().where(News.sample_id == s.id)):
                    news_id = news[0]
                    session.execute(
                        LinkUserNews.__table__.delete().where(LinkUserNews.news_id == news_id)
                    )
                session.execute(News.__table__.delete().where(News.sample_id == s.id))
                # and delete all corresponding shares
                session.execute(Share.__table__.delete().where(Share.sample_id == s.id))
                # NB: if another user has children underneath this sample, they have been taken care of previously
                #     idem if another user has mounted samples underneath this sample
            else:
                # otherwise it belongs to someone else and we move it back to that person's root
                session.execute(
                    Sample.__table__.update().values(parent_id=0).where(Sample.id == s.id)
                )
                # If there is some news associated with the sample or a subsample, this is not really an issue.
                # Everybody who has access to the sample - and the person who created the news, will still see
                # the news - but the person who created the news will not be able to access the sample (and therefore
                # not be able to deactivate the news). Two possible solutions:
                # - wait for the news to expire
                # - give the user access again so he/she can deactivate the news
                # TODO: careful with duplicate sample names here

    # delete all corresponding shares
    session.execute(Share.__table__.delete().where(Share.sample_id == sample.id))

    # delete all corresponding news
    for news in session.execute(News.__table__.select().where(News.sample_id == sample.id)):
        news_id = news[0]
        session.execute(LinkUserNews.__table__.delete().where(LinkUserNews.news_id == news_id))
    session.execute(News.__table__.delete().where(News.sample_id == sample.id))

    recursive(sample)


def deleted_share_handler(session, share):
    def recursive(sample):
        # move samples mounted here back to the root for the user whose share we remove
        session.execute(
            Share.__table__.update()
            .values(mountpoint_id=0)
            .where(Share.user == share.user and Share.mountpoint == sample)
        )

        # go down the hierarchy and perform the same operations
        for s in sample.children:
            recursive(s)

            # check if child or mounted sample belongs to the user whose share we remove and move it back to his tree
            if s.owner == share.user:
                session.execute(
                    Sample.__table__.update().values(parent_id=0).where(Sample.id == s.id)
                )
                # If there is some news associated with the sample or a subsample, this is not really an issue.
                # Everybody who has access to the sample - and the person who created the news, will still see
                # the news - but the person who created the news will not be able to access the sample (and therefore
                # not be able to deactivate the news). Two possible solutions:
                # - wait for the news to expire
                # - give the user access again so he/she can deactivate the news
                # TODO: careful with duplicate sample names here

    recursive(share.sample)


# https://stackoverflow.com/questions/13693872/can-sqlalchemy-events-be-used-to-update-a-denormalized-data-cache/13765857#13765857
# https://github.com/pallets/flask-sqlalchemy/issues/182
def after_flush(session, flush_context):
    """- check for any deleted samples or shares
    NB: This had to be done after the flush, because if a parent sample / mountpoint was deleted,
    the database would automatically set the corresponding foreign keys to NULL. Not sure if this
    still applies since we are not really deleting samples anymore.
    """
    for obj in session.dirty:
        if isinstance(obj, Sample) and obj.isdeleted:  # detected sample deletion
            deleted_sample_handler(session, obj)

    for obj in session.deleted:
        if isinstance(obj, Share):  # detected share deletion
            deleted_share_handler(session, obj)


event.listen(SignallingSession, "after_flush", after_flush)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)
    is_admin = db.Column(db.Boolean())
    samples = db.relationship("Sample", backref="owner")
    actions = db.relationship("Action", backref="owner")
    shares = db.relationship("Share", backref="user")
    uploads = db.relationship("Upload", backref="user")
    activity = db.relationship("Activity", backref="user")
    heir_id = db.Column(
        db.Integer, db.ForeignKey("users.id")
    )  # ID of the user who inherits this users data

    inheritance = db.relationship(
        "User", backref=db.backref("heir", remote_side=[id])
    )  # Users who gave their data to this one

    def __repr__(self):
        return "<User %r>" % self.username

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_reset_token(self, expiration=3600):
        s = Serializer(app.config["SECRET_KEY"], expiration)
        return s.dumps({"reset": self.id}).decode("utf-8")

    @staticmethod
    def reset_password(token, new_password):
        s = Serializer(app.config["SECRET_KEY"])
        try:
            data = s.loads(token.encode("utf-8"))
        except:
            return False
        user = User.query.get(data.get("reset"))
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        return True

    @property
    def directshares(self):
        """determine the user's direct shares that are not mounted anywhere in his tree
        (i.e. they are at the top level)
        """
        return [
            s.sample
            for s in self.shares
            if s.mountpoint_id == 0
            and s.sample.is_accessible_for(self, direct_only=True)
            and not s.sample.isdeleted
        ]

    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode("utf-8")
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Sample(db.Model):
    __tablename__ = "samples"
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    name = db.Column(db.String(SAMPLE_NAME_LENGTH))
    parent_id = db.Column(db.Integer, db.ForeignKey("samples.id"))
    image = db.Column(db.String(300))  # <----------- a changer
    description = db.Column(db.UnicodeText)
    isarchived = db.Column(db.Boolean)
    isdeleted = db.Column(db.Boolean)
    # in collaborative samples, all sharing users can edit all actions
    iscollaborative = db.Column(db.Boolean)
    last_modified = db.Column(db.DateTime)

    # NB: the cascade delete for shares and actions is no longer used because we delete samples by
    #     setting isdeleted to True
    children = db.relationship("Sample", backref=db.backref("parent", remote_side=[id]))
    shares = db.relationship(
        "Share", backref="sample", foreign_keys="Share.sample_id", cascade="delete"
    )
    mountedshares = db.relationship(
        "Share", backref="mountpoint", foreign_keys="Share.mountpoint_id"
    )
    actions = db.relationship("Action", backref="sample", cascade="delete")

    news = db.relationship("News", backref="sample", cascade="delete")
    activity = db.relationship("Activity", backref="sample")

    def __setattr__(self, name, value):
        if name == "name":
            if (
                value != self.name
                and self.query.filter_by(
                    owner=current_user, parent_id=self.parent_id, name=value, isdeleted=False
                ).all()
            ):
                raise Exception("You already have a sample with this name on this hierarchy level.")
        if name == "parent_id":
            if (
                value != self.parent_id
                and self.name is not None
                and self.query.filter_by(
                    owner=current_user, parent_id=value, name=self.name, isdeleted=False
                ).all()
            ):
                raise Exception("You already have a sample with this name on this hierarchy level.")
        super(Sample, self).__setattr__(name, value)

    def __repr__(self):
        return "<Sample %r>" % self.name

    def is_accessible_for(self, user, indirect_only=False, direct_only=False):
        """go through the owner and shares of this sample and check in the hierarchy (i.e. all parents)
        if it can be accessed by user

        - if indirect_only is True, only look for indirect shares, i.e. parent shares
        - if direct_only is True, only look for direct shares

        indirect sharing has priority over direct sharing in order to avoid clogging up the hierarchy
        """

        # check for invalid flag usage
        if indirect_only and direct_only:
            raise Exception("Choose either indirect_only or direct_only or neither")

        # if looking for shared access, check first if user owns the sample
        if (indirect_only or direct_only) and self.owner == user:
            return False

        if direct_only:
            return user in [s.user for s in self.shares] and not self.is_accessible_for(
                user, indirect_only=True
            )

        parent = self.parent if indirect_only else self
        shares = []
        while parent:
            shares.append(parent.owner)
            shares.extend([s.user for s in parent.shares])
            parent = parent.parent
        return user in shares

    @property
    def mountedsamples(self):
        """make a list of samples that are mounted in this one by the current user"""

        return [
            s.sample
            for s in self.mountedshares
            if s.user == current_user  # make sure it's mounted by the current user
            and s.sample.is_accessible_for(
                current_user, direct_only=True
            )  # exclude indirect shares
            and not s.sample.isdeleted
        ]

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
    __tablename__ = "actions"
    id = db.Column(db.Integer, primary_key=True)
    ordnum = db.Column(db.Integer)  # used to manipulate order of actions without modifying IDs
    datecreated = db.Column(
        db.Date
    )  # used to keep track of when actions are created (user cannot modify this)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    timestamp = db.Column(db.Date)
    sample_id = db.Column(db.Integer, db.ForeignKey("samples.id"))
    news_id = db.Column(db.Integer, db.ForeignKey("news.id"))
    description = db.Column(db.UnicodeText)

    news = db.relationship("News", backref="action", cascade="delete")

    def __repr__(self):
        return "<Action %r>" % self.id

    def has_read_access(self, user):
        if self.owner == user:
            return True

        if self.sample.iscollaborative and self.sample.is_accessible_for(user):
            return True

        return False

    def has_write_access(self, user):
        return self.has_read_access(user)


class News(db.Model):
    __tablename__ = "news"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.UnicodeText)
    content = db.Column(db.UnicodeText)

    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    sender = db.relationship("User", foreign_keys=[sender_id])

    # recipient can be either all users, a specific user, or all users who share a given sample
    recipient_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    sample_id = db.Column(db.Integer, db.ForeignKey("samples.id"))

    published = db.Column(db.Date)
    expires = db.Column(db.Date)

    # action = db.relationship('Action', backref="news")
    recipients = db.relationship(
        "LinkUserNews", backref="news", foreign_keys="LinkUserNews.news_id", cascade="delete"
    )

    def dispatch(self):
        # remove all existing links
        links = LinkUserNews.query.filter_by(news_id=self.id).all()
        for link in links:
            db.session.delete(link)
        db.session.commit()

        # construct list of recipients
        recipients = []
        if self.sample:
            # dispatch the news to all users who have access to this sample, i.e.
            # all users who share the sample directly or who share a parent sample
            recipients.append(self.sample.owner)

            sample = self.sample
            while sample:
                recipients.append(sample.owner)
                recipients.extend([s.user for s in sample.shares])
                sample = sample.parent

        # remove duplicates from recipients
        recipients = set(recipients)

        # create links
        for recipient in recipients:
            link = LinkUserNews(user_id=recipient.id, news_id=self.id)
            db.session.add(link)
            db.session.commit()

    def render_content(self):
        # TODO: here we could also support other prefixes
        if not self.content or not self.content.startswith("action:"):
            return "Invalid news content"

        actionid = int(self.content[len("action:") :])
        action = Action.query.get(actionid)
        if action is None:
            return "Invalid action link"

        return f"""{action.timestamp} <i>{action.owner.username}</i> {action.description}"""


class LinkUserNews(db.Model):
    __tablename__ = "linkusernews"
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    news_id = db.Column(db.Integer, db.ForeignKey("news.id"))

    user = db.relationship("User", backref="news_links")


class SMBResource(db.Model):
    __tablename__ = "smbresources"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    servername = db.Column(db.String(64))
    serveraddr = db.Column(db.String(64))
    sharename = db.Column(db.String(64))
    path = db.Column(db.String(256))
    userid = db.Column(db.String(64))
    password = db.Column(db.String(64))

    def __repr__(self):
        return "<SMBResource %r>" % self.id


class Share(db.Model):
    __tablename__ = "shares"
    id = db.Column(db.Integer, primary_key=True)
    sample_id = db.Column(db.Integer, db.ForeignKey("samples.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    mountpoint_id = db.Column(db.Integer, db.ForeignKey("samples.id"))

    def __repr__(self):
        return "<Share %r>" % self.id


class Upload(db.Model):
    __tablename__ = "uploads"
    id = db.Column(db.Integer, primary_key=True)
    ext = db.Column(db.String(10))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    source = db.Column(db.String(256))
    size = db.Column(db.Integer)
    hash = db.Column(db.String(64))

    def __repr__(self):
        return "<Upload %r>" % self.id


class Activity(db.Model):
    __tablename__ = "activity"
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    sample_id = db.Column(db.Integer, db.ForeignKey("samples.id"))
    type_id = db.Column(db.Integer, db.ForeignKey("activitytypes.id"))
    description = db.Column(db.UnicodeText)

    def __repr__(self):
        return "<Activity %r>" % self.id


# Since the activity table will probably contain a lot of entries, the activity
# type, e.g. "update:sample:description" should be encoded as an integer ID
# referring to this table. When the database models are amended, the supported
# activity types will be adapted automatically in app/__init__.py based on the
# supported_targets dictionary in app/main/views.py.
class ActivityType(db.Model):
    __tablename__ = "activitytypes"
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(256))

    activity = db.relationship("Activity", backref="type")

    def __repr__(self):
        return "<ActivityType %r>" % self.description


def record_activity(type, user=None, sample=None, description=None, commit=False):
    timestamp = datetime.now()
    atype = ActivityType.query.filter_by(description=type).first()
    if atype is None:
        raise Exception("Unknown activity type: " + type)
    activity = Activity(
        timestamp=timestamp,
        user_id=user.id if user is not None else 0,
        sample_id=sample.id if sample is not None else 0,
        type_id=atype.id,
        description=description,
    )
    db.session.add(activity)
    if sample is not None:
        sample.last_modified = timestamp
    if commit:
        db.session.commit()
