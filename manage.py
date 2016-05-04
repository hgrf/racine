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

##### TEMPORARY MODIFICATION TO CALCULATE SHA-256 HASHS FOR ALL PREVIOUSLY UPLOADED FILES
from app.models import Upload
import hashlib

@manager.command
def calcuploadhashs():
    uploads = Upload.query.all()
    for u in uploads:
        try:
            file_obj = open(os.path.join(app.config['UPLOAD_FOLDER'], str(u.id) + '.' + u.ext), 'rb')
            u.hash = hashlib.sha256(file_obj.read()).hexdigest()
            db.session.commit()
            file_obj.close()
        except IOError:
            print "File not found. Removing upload ID=", u.id, " source=", u.source
            db.session.delete(u)
            db.session.commit()

##### END OF TEMPORARY MODIFICATION


if __name__ == '__main__':
    manager.run()