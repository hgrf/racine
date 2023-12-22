from datetime import datetime

from ..common import db


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
# activity types will be adapted automatically based on the supported_targets
# dictionary in app/api/fields.py.
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
