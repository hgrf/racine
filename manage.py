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


if __name__ == '__main__':
    manager.run()