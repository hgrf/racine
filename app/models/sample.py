from .share import Share
from .user import current_user
from .. import db

SAMPLE_NAME_LENGTH = 64


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
                    owner=current_user(), parent_id=self.parent_id, name=value, isdeleted=False
                ).all()
            ):
                raise Exception("You already have a sample with this name on this hierarchy level.")
        if name == "parent_id":
            if (
                value != self.parent_id
                and self.name is not None
                and self.query.filter_by(
                    owner=current_user(), parent_id=value, name=self.name, isdeleted=False
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
            if s.user == current_user()  # make sure it's mounted by the current user
            and s.sample.is_accessible_for(
                current_user, direct_only=True
            )  # exclude indirect shares
            and not s.sample.isdeleted
        ]

    @property
    def logical_parent(self):
        # determine the sample's logical parent in the current user's tree (i.e. the parent or
        # the mountpoint)

        # first find out if the sample belongs to the current user (in this case just return
        # the real parent)
        if self.owner == current_user():
            return self.parent

        # if the sample is indirectly shared with the current user, also return the real parent
        if self.is_accessible_for(current_user(), indirect_only=True):
            return self.parent

        # if the sample is directly shared with the current user, return the mount point
        if self.is_accessible_for(current_user(), direct_only=True):
            share = Share.query.filter_by(sample=self, user=current_user()).first()
            return share.mountpoint
