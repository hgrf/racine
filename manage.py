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

# helper function to find duplicate image entries
from app.models import Upload
import hashlib

@manager.command
def findduplicates():
    # could probably do this much better with an elegant DB query, but
    # I'll go for the quick and dirty solution because I have to go
    # drink beer
    uploads = Upload.query.all()
    for i1 in range(len(uploads)):
        u1 = uploads[i1]
        # check file size
        stat = os.stat(os.path.join(app.config['UPLOAD_FOLDER'], str(u1.id) + '.' + u1.ext))
        if stat.st_size == 0:
            print "Upload ID {} is an empty file.".format(u1.id)
            continue
        for i2 in range(i1, len(uploads)):          # only iterate through rest of uploads (avoid double counting)
            u2 = uploads[i2]
            if u1.id == u2.id: continue
            if u1.hash == u2.hash: print "Upload ID {} is a duplicate of {}.".format(u1.id, u2.id)

# helper function to find all image references
from app.models import Action, Sample

def handle_img(loc, src):
    if src[:15] == '/browser/ulimg/':
        print loc, "uploaded image ID", src[15:]
    elif src[:5] == 'data:':
        print loc, "base64 image"
    else:
        print loc, "other source:", src

def handle_img_tags(text, user, itemid):
    i = -1
    while True:
        i = text.find('<img', i+1)
        if i != -1:
            j = text.find('>', i)   # end of img tag
            k = text.find('src=', i)
            assert k<j                            # make sure the src attr. belongs to the img tag
            l = k+4
            invcomma = text[l]
            m = text.find(invcomma, l+1)
            assert m<j                            # make sure the string ends before the end of the img tag
            handle_img("{} position {}".format(itemid, i), text[l+1:m])
        else:
            break

    return text

@manager.command
def findimgrefs():
    actions = Action.query.all()
    for action in actions:
        action.description = handle_img_tags(action.description, action.owner, "action {}".format(action.id))
        db.session.commit()

    samples = Sample.query.all()
    for sample in samples:
        if sample.image is not None:
            handle_img("sample {}".format(sample.id), sample.image)
        if sample.description is not None:
            handle_img_tags(sample.description, sample.owner, "sample {}".format(sample.id))

if __name__ == '__main__':
    manager.run()