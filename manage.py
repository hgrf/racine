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


###################  TEMPORARY MODIFICATION THAT WILL CARRY OUT DB MODIFICATIONS
from app.models import Action, Sample, SMBResource, Upload
import socket
from smb.SMBConnection import SMBConnection

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_extension(filename):
    return filename.rsplit('.', 1)[1].lower()

def connect_to_SMBResource(resource):
    # set up SMB connection
    client_machine_name = "SampleManagerWeb"
    try:
        server_ip = socket.gethostbyname(resource.serveraddr)
    except:     # if host unknown
        return None, False
    # need to convert unicode -> string apparently... (checked with print type(resource.servername))
    conn = SMBConnection(str(resource.userid), str(resource.password), client_machine_name, str(resource.servername), use_ntlm_v2=True)
    try:
        connected = conn.connect(server_ip, 139, timeout=1) # 1 second timeout
    except:
        connected = False
    return conn, connected

def store_img(orgsrc, user):
    # get rid of /browser/img/
    if not orgsrc[:13] == '/browser/img/':
        return orgsrc, 'wrong prefix'         # nothing to do here if the path does not start with /browser/img
    src = orgsrc[13:]                         # cut off the /browser/img part

    # process path of SMB resource
    resource = SMBResource.query.filter_by(name=src.split("/")[0]).first()
    if resource is None:
        return orgsrc, 'resource does not exist'
    address_prefix = "" if resource.path == None else resource.path
    address_in_resource = src[src.find("/")+1:]
    address_on_server = address_prefix + ("/" if address_prefix != "" else "") + address_in_resource
    filename = address_in_resource.split("/")[-1]

    if allowed_file(filename):
        dbentry = Upload(user=user, source='smb:'+src, ext=get_extension(filename))
        db.session.add(dbentry)
        db.session.commit()

        conn, connected = connect_to_SMBResource(resource)
        if not connected:
            return orgsrc, "Could not connect to SMBResource: "+resource.name

        file_obj = open(os.path.join(app.config['UPLOAD_FOLDER'], str(dbentry.id)+'.'+dbentry.ext), 'wb')
        try:
            file_attributes, filesize = conn.retrieveFile(resource.sharename, address_on_server, file_obj)
        except: # if we have any problem retrieving the file
            return orgsrc, "Could not retrieve file: "+resource.name+'/'+address_on_server

        uploadurl = "/browser/ulimg/"+str(dbentry.id)
        return uploadurl, 'OK'

    return orgsrc, 'filename not allowed'

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
            print "{} position {}: {}".format(itemid, i, text[l+1:m])
            src, msg = store_img(text[l+1:m], user)
            print "Result: ", msg, " // new src: ", src
            if msg == 'OK':
                text = text[:l+1]+src+text[m:]
        else:
            break

    return text

@manager.command
def uploadhelper():
    '''
    This helper function automatically updates any img tags in sample or action descriptions and also the sample
    image source. The reason for this modification is that the previous /browser/img/<path> shall no longer be used
    to access images. Images shall from now on be uploaded to the MSM server, even if they come from SMB resources.

    In principle, this helper function is really easy to use:
    1 ) Back up your database and the upload folder.
    2 ) CD into the MSM directory, deactivate any production server instances, activate the virtual environment
        and type:
            python manage.py uploadhelper
    3 ) Ignore any entries where the result is "OK" or "wrong prefix", all other entries should be checked indi-
        vidually. Then test the new behaviour and see if images were successfully updated.
    '''

    actions = Action.query.all()
    for action in actions:
        action.description = handle_img_tags(action.description, action.owner, "action {}".format(action.id))
        db.session.commit()

    samples = Sample.query.all()
    for sample in samples:
        if sample.image is not None:
            print "sample {} image: {}".format(sample.id, sample.image)
            src, msg = store_img(sample.image, sample.owner)
            print "Result: ", msg, " // new src: ", src
            if msg == 'OK':
                sample.image = src
                db.session.commit()
        if sample.description is None: continue
        handle_img_tags(sample.description, sample.owner, "sample {}".format(sample.id))

###################  END OF TEMPORARY MODIFICATION



if __name__ == '__main__':
    manager.run()