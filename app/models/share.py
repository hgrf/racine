from .. import db


class Share(db.Model):
    __tablename__ = "shares"
    id = db.Column(db.Integer, primary_key=True)
    sample_id = db.Column(db.Integer, db.ForeignKey("samples.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    mountpoint_id = db.Column(db.Integer, db.ForeignKey("samples.id"))

    def __repr__(self):
        return "<Share %r>" % self.id
