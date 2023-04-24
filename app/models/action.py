from .. import db


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
        # actions inherit read permissions from their sample
        return self.sample.is_accessible_for(user)

    def has_write_access(self, user):
        return (user == self.owner) or (
            self.sample.iscollaborative and self.sample.is_accessible_for(user)
        )
