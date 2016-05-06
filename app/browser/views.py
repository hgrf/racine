from flask import render_template, send_file, request, redirect, url_for, send_from_directory, jsonify
from flask_login import current_user
from flask import current_app as app
from smb.SMBConnection import SMBConnection
from .. import db
from ..models import SMBResource, Sample, Upload
import socket
import os
from . import browser
import tempfile
import io
import hashlib

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

class FileTile:
    name = ""
    ext = ""
    image = ""

class ResourceTile:
    name = ""
    available = True        # set to false if connection to resource cannot be established
    hasuserfolder = False
    hassamplefolder = False

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

def assemble_path(items):
    path = ""
    for item in items:
        if item == None or item == "" or item == "/":
            continue
        path = path+item+"/"
    return path.rstrip('/')


@browser.route('/', defaults={'address': ''})
@browser.route('/<path:address>')
def imagebrowser(address):
    # TODO: make sure resource names do not contain / or are .. or stuff like that

    # basic config stuff
    image_extensions = [".jpg", ".jpeg", ".png"]

    # find out from which sample the browser was opened
    if request.args.get("sample") is None:
        sample = None
    else:
        sample = Sample.query.filter_by(id=int(request.args.get("sample"))).first()

    # process address (1)
    address = address.rstrip('/')

    if(address == ""):  # in this case we need to present choice of resources
        resources=[]
        resourcetable = SMBResource.query.all()
        for resource in resourcetable:
            r = ResourceTile()
            r.name = resource.name
            conn, connected = connect_to_SMBResource(resource)
            if not connected:
                r.name += " (N/A)"
                r.available = False
                resources.append(r)
                continue
            # find user/sample folders
            if sample is not None:
                for i in conn.listPath(resource.sharename, resource.path if resource.path != None else ""):
                    if i.isDirectory and i.filename == sample.owner.username:
                        r.hasuserfolder = True
                        for j in conn.listPath(resource.sharename, assemble_path([resource.path, i.filename])):
                            if j.isDirectory and j.filename == sample.name:
                                r.hassamplefolder = True
                                break
                        break
            conn.close()
            resources.append(r)
        return render_template('browser.html', files=[], folders=[], resources=resources, sample=sample, callback=request.args.get('CKEditorFuncNum'))

    # process address (2)
    resource = SMBResource.query.filter_by(name=address.split("/")[0]).first()
    address_prefix = "" if resource.path == None else resource.path
    address_in_resource = "" if address.find("/") == -1 else address[address.find("/")+1:]
    address_on_server = address_prefix + ("/" if address_prefix != "" and address_in_resource != "" else "") + address_in_resource

    conn, connected = connect_to_SMBResource(resource)
    if not connected:
        return render_template('browser.html', notconnected=True)

    # list files and folders in current path
    files = []
    folders = []
    for i in conn.listPath(resource.sharename, address_on_server):
        if i.filename == '.':
            continue
        #if i.filename == ".." and address == '': should not be problem anymore as we do resource navigation separately
        #    continue
        f = FileTile()
        f.name, f.ext = os.path.splitext(i.filename)
        if not i.isDirectory:
            if f.ext.lower() in image_extensions:
                f.image = "/browser/img/" + address + (
                    "" if address == "" else "/") + f.name + f.ext  # will at some point cause problems with big image files, consider caching compressed icons
            else:
                f.image = "/static/file.png"
            files.append(f)
        else:
            f.image = "/static/folder.png"
            folders.append(f)

    files = sorted(files, key=lambda f: f.name)
    folders = sorted(folders, key=lambda f: f.name)
    return render_template('browser.html', files=files, folders=folders, resources=[], sample=sample, address=address, callback=request.args.get('CKEditorFuncNum'))


@browser.route('/img/<path:image>')
def browserimage(image):
    '''
    This function will become obsolete once all images from SMB resources have been uploaded to MSM server.
    '''
    resource = SMBResource.query.filter_by(name=image.split("/")[0]).first()

    address_prefix = "" if resource.path == None else resource.path
    address_in_resource = image[image.find("/")+1:]
    address_on_server = address_prefix + ("/" if address_prefix != "" else "") + address_in_resource

    conn, connected = connect_to_SMBResource(resource)
    if not connected:
        app.logger.error("Could not connect to SMBResource: "+resource.name)
        return ''

    file_obj = tempfile.NamedTemporaryFile()
    try:
        file_attributes, filesize = conn.retrieveFile(resource.sharename, address_on_server, file_obj)
    except: # if we have any problem retrieving the file
        app.logger.error("Could not retrieve file: "+resource.name+'/'+address_on_server)
        return ''

    file_obj.seek(0)
    image_binary = file_obj.read()

    file_obj.close()

    return send_file(io.BytesIO(image_binary))

@browser.route('/ulimg/<image>')
def uploadedimage(image):
    dbentry = Upload.query.filter_by(id=image).first()
    return send_from_directory(app.config['UPLOAD_FOLDER'], str(dbentry.id)+'.'+dbentry.ext)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_extension(filename):
    return filename.rsplit('.', 1)[1].lower()

@browser.route('/upload', methods=['POST'])
def uploadfile():
    if request.args.get("sample") is None:
        sample=None
    else:
        sample=Sample.query.filter_by(id=int(request.args.get("sample"))).first()

    file = request.files['file']
    if file and allowed_file(file.filename):
        dbentry = Upload(user=current_user, source='ul:'+file.filename, ext=get_extension(file.filename))

        db.session.add(dbentry)
        db.session.commit()
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], str(dbentry.id)+'.'+dbentry.ext))

        dbentry.size = os.stat(os.path.join(app.config['UPLOAD_FOLDER'], str(dbentry.id) + '.' + dbentry.ext)).st_size
        file_obj = open(os.path.join(app.config['UPLOAD_FOLDER'], str(dbentry.id) + '.' + dbentry.ext), 'rb')
        dbentry.hash = hashlib.sha256(file_obj.read()).hexdigest()
        db.session.commit()
        file_obj.close()

        uploadurl = url_for('.uploadedimage', image=str(dbentry.id))
        return render_template('browser.html', files=[], folders=[], resources=[], sample=sample, callback=request.args.get('CKEditorFuncNum'), uploadurl=uploadurl)

    return redirect(url_for('browser'))

@browser.route('/savefromsmb', methods=['POST'])
def savefromsmb():
    src = request.form.get('src')

    # get rid of /browser/img/
    if not src[:13] == '/browser/img/':
        return jsonify(code=1)
    src = src[13:]

    # process path of SMB resource
    resource = SMBResource.query.filter_by(name=src.split("/")[0]).first()
    address_prefix = "" if resource.path == None else resource.path
    address_in_resource = src[src.find("/")+1:]
    address_on_server = address_prefix + ("/" if address_prefix != "" else "") + address_in_resource
    filename = address_in_resource.split("/")[-1]

    if allowed_file(filename):
        dbentry = Upload(user=current_user, source='smb:'+src, ext=get_extension(filename))
        db.session.add(dbentry)
        db.session.commit()

        conn, connected = connect_to_SMBResource(resource)
        if not connected:
            app.logger.error("Could not connect to SMBResource: "+resource.name)
            return ''

        file_obj = open(os.path.join(app.config['UPLOAD_FOLDER'], str(dbentry.id)+'.'+dbentry.ext), 'wb')
        try:
            file_attributes, filesize = conn.retrieveFile(resource.sharename, address_on_server, file_obj)
        except: # if we have any problem retrieving the file
            app.logger.error("Could not retrieve file: "+resource.name+'/'+address_on_server)
            return ''

        file_obj = open(os.path.join(app.config['UPLOAD_FOLDER'], str(dbentry.id) + '.' + dbentry.ext), 'rb')
        dbentry.hash = hashlib.sha256(file_obj.read()).hexdigest()
        dbentry.size = filesize
        db.session.commit()
        file_obj.close()

        uploadurl = url_for('.uploadedimage', image=str(dbentry.id))
        return jsonify(code=0, uploadurl=uploadurl)

    return jsonify(code=1)
