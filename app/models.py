from . import db

SAMPLE_NAME_LENGTH = 64


class SampleType(db.Model):
    __tablename__ = 'sampletypes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    samples = db.relationship('Sample', backref='sampletype')

    def __repr__(self):
        return '<SampleType %r>' % self.name


class Sample(db.Model):
    __tablename__ = 'samples'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(SAMPLE_NAME_LENGTH), unique=True, index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('samples.id'))
    sampletype_id = db.Column(db.Integer, db.ForeignKey('sampletypes.id'))
    image = db.Column(db.String(300))  # <----------- a changer

    mwidth = db.Column(db.Integer)  # matrix width (for children)
    mheight = db.Column(db.Integer)  # matrix height (for children)
    mx = db.Column(db.Integer)  # matrix x position (for parent)
    my = db.Column(db.Integer)  # matrix y position (for parent)

    children = db.relationship('Sample', backref=db.backref('parent', remote_side=[id]))
    actions = db.relationship('Action', backref='sample', cascade="delete")

    def __repr__(self):
        return '<Sample %r>' % self.name


class ActionType(db.Model):
    __tablename__ = 'actiontypes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    actions = db.relationship('Action', backref='actiontype')

    def __repr__(self):
        return '<ActionType %r>' % self.name


class Action(db.Model):
    __tablename__ = 'actions'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.Date)
    sample_id = db.Column(db.Integer, db.ForeignKey('samples.id'))
    actiontype_id = db.Column(db.Integer, db.ForeignKey('actiontypes.id'))
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
    userid = db.Column(db.String(64))
    password = db.Column(db.String(64))

    def __repr__(self):
        return '<SMBResource %r>' % self.id