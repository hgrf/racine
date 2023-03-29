from flask_login import current_user
from flask_sqlalchemy import SignallingSession
from sqlalchemy import event

from .. import db
from .action import Action
from .activity import Activity, ActivityType, record_activity  # noqa: F401
from .news import News, LinkUserNews
from .user import token_auth, User  # noqa: F401

SAMPLE_NAME_LENGTH = 64


def deleted_sample_handler(session, sample):
    def recursive(sample):
        user = token_auth.current_user() or current_user

        # move everything that is mounted here back to the root
        session.execute(
            Share.__table__.update().values(mountpoint_id=0).where(Share.mountpoint_id == sample.id)
        )

        # go down the hierarchy and perform the same operations
        for s in sample.children:
            recursive(s)

            if s.owner == user:
                # if the sample down the hierarchy belongs to the current user,
                # also mark it as deleted
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
                # NB: if another user has children underneath this sample, they have been taken
                #     care of previously; idem if another user has mounted samples underneath
                #     this sample
            else:
                # otherwise it belongs to someone else and we move it back to that person's root
                session.execute(
                    Sample.__table__.update().values(parent_id=0).where(Sample.id == s.id)
                )
                # If there is some news associated with the sample or a subsample, this is not
                # really an issue. Everybody who has access to the sample - and the person who
                # created the news, will still see the news - but the person who created the
                # news will not be able to access the sample (and therefore not be able to
                # deactivate the news). Two possible solutions:
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

            # check if child or mounted sample belongs to the user whose share we remove
            # and move it back to his tree
            if s.owner == share.user:
                session.execute(
                    Sample.__table__.update().values(parent_id=0).where(Sample.id == s.id)
                )
                # If there is some news associated with the sample or a subsample, this is not
                # really an issue. Everybody who has access to the sample - and the person who
                # created the news, will still see the news - but the person who created the
                # news will not be able to access the sample (and therefore not be able to
                # deactivate the news). Two possible solutions:
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
        user = token_auth.current_user() or current_user
        if name == "name":
            if (
                value != self.name
                and self.query.filter_by(
                    owner=user, parent_id=self.parent_id, name=value, isdeleted=False
                ).all()
            ):
                raise Exception("You already have a sample with this name on this hierarchy level.")
        if name == "parent_id":
            if (
                value != self.parent_id
                and self.name is not None
                and self.query.filter_by(
                    owner=user, parent_id=value, name=self.name, isdeleted=False
                ).all()
            ):
                raise Exception("You already have a sample with this name on this hierarchy level.")
        super(Sample, self).__setattr__(name, value)

    def __repr__(self):
        return "<Sample %r>" % self.name

    def is_accessible_for(self, user, indirect_only=False, direct_only=False):
        """go through the owner and shares of this sample and check in the hierarchy
        (i.e. all parents) if it can be accessed by user

        - if indirect_only is True, only look for indirect shares, i.e. parent shares
        - if direct_only is True, only look for direct shares

        indirect sharing has priority over direct sharing in order to avoid clogging
        up the hierarchy
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
        user = token_auth.current_user() or current_user
        # determine the sample's logical parent in the current user's tree (i.e. the parent or
        # the mountpoint)

        # first find out if the sample belongs to the current user (in this case just return
        # the real parent)
        if self.owner == user:
            return self.parent

        # if the sample is indirectly shared with the current user, also return the real parent
        if self.is_accessible_for(user, indirect_only=True):
            return self.parent

        # if the sample is directly shared with the current user, return the mount point
        if self.is_accessible_for(user, direct_only=True):
            share = Share.query.filter_by(sample=self, user=user).first()
            return share.mountpoint


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
