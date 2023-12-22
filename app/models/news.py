from .action import Action
from ..common import db


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
