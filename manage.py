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
def make_previews():
    """ Helper function to generate previews (smaller versions of images) for all existing
        images on the server.
    """
    from app.models import Upload
    from app.browser.views import make_preview
    from PIL import Image
    import warnings

    extensions = set(['.png', '.jpg', '.jpeg', '.bmp'])
    uploads = Upload.query.all()
    progress = 1                    # progress in units of 10%
    for i, upload in enumerate(uploads):
        # show progress
        if float(i)/len(uploads)*100/10 > progress:
            print "Progress: "+str(progress*10)+"%"
            progress += 1

        path = os.path.join(app.config['UPLOAD_FOLDER'], str(upload.id) + '.' + upload.ext)
        if os.path.splitext(path)[1].lower() not in extensions:
            continue            # ignore non-image files
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            continue            # ignore lost uploads

        # load image
        try:
            with warnings.catch_warnings(record=True) as ws:
                warnings.simplefilter("always")
                image = Image.open(path)
                if len(ws):
                    print "Warnings for upload "+str(upload.id)+":"
                    for w in ws:
                        print '   ', w.message
        except Exception as e:
            print "Could not load image or make preview for upload "+str(upload.id)+":", e
            continue

        # create preview
        try:
            with warnings.catch_warnings(record=True) as ws:
                warnings.simplefilter("always")
                make_preview(upload, image)
                if len(ws):
                    print "Warnings for upload "+str(upload.id)+":"
                    for w in ws:
                        print '   ', w.message
        except Exception as e:
            print "Could not make preview for upload "+str(upload.id)+":", e


if __name__ == '__main__':
    manager.run()