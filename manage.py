#!/usr/bin/env python
import os
from app import create_app, db
from app.models import User
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, User=User)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

@manager.command
def uploadsizes():
    '''
    Puts filesizes of previous uploads in database.
    '''
    from app.models import Upload

    uploads = Upload.query.all()
    for u in uploads:
        u.size = os.stat(os.path.join(app.config['UPLOAD_FOLDER'], str(u.id) + '.' + u.ext)).st_size
        db.session.commit()

###################  TEMPORARY MODIFICATION THAT WILL CARRY OUT DB MODIFICATIONS
from app.models import Action, Sample, SMBResource, Upload

def handle_a_tags(text, itemid):
    i = -1
    while True:
        i = text.find('<a', i+1)
        if i != -1:
            j = text.find('>', i)   # end of a tag
            k = text.find('href=', i)
            assert k<j                            # make sure the href attr. belongs to the a tag
            l = k+5
            invcomma = text[l]
            m = text.find(invcomma, l+1)
            assert m<j                            # make sure the string ends before the end of the a tag
            print "{} position {}: {}".format(itemid, i, text[l+1:m])

            # remove leading http(s)://server/ for affected links
            if text[l+1:].startswith('http'):
                if text[l+5] == 's':        # https
                    n = text.find('/', l+9)
                else:
                    n = text.find('/', l+8)
                text = text[:l+1]+text[m:n]+text[n:]
        else:
            break

    return text

@manager.command
def linkhelper():
    '''
    This helper function automatically searches hyperlinks in sample and action descriptions.
    '''

    actions = Action.query.all()
    for action in actions:
        action.description = handle_a_tags(action.description, "action {}".format(action.id))
        db.session.commit()

    samples = Sample.query.all()
    for sample in samples:
        if sample.description is None: continue
        sample.description = handle_a_tags(sample.description, "sample {}".format(sample.id))
        db.session.commit()

###################  END OF TEMPORARY MODIFICATION


if __name__ == '__main__':
    manager.run()