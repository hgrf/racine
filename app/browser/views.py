from flask import render_template, send_file
from smb.SMBConnection import SMBConnection
from ..models import SMBResource
import socket
import tempfile
import os
import io
from . import browser


class FileTile:
    name = ""
    ext = ""
    image = ""


@browser.route('', defaults={'address': ''})
@browser.route('/<path:address>')
def imagebrowser(address):
    # for the moment we'll only use the first database entry
    # TODO: add possibility to choose from SMBResources
    resource = SMBResource.query.filter_by(id=1).first()
    client_machine_name = "SampleManagerWeb"
    server_ip = socket.gethostbyname(resource.serveraddr)
    image_extensions = [".jpg", ".jpeg", ".png"]
    # need to convert unicode -> string apparently... (checked with print type(resource.servername))
    conn = SMBConnection(str(resource.userid), str(resource.password), client_machine_name, str(resource.servername),
                         use_ntlm_v2=True)
    assert conn.connect(server_ip, 139)

    files = []
    folders = []
    for i in conn.listPath(resource.sharename, address):
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
    return render_template('browserframe.html', files=files, folders=folders, address=address)


@browser.route('/img/<path:image>')
def browserimage(image):
    # for the moment we'll only use the first database entry
    # TODO: add possibility to choose from SMBResources
    resource = SMBResource.query.filter_by(id=1).first()
    client_machine_name = "SampleManagerWeb"
    server_ip = socket.gethostbyname(resource.serveraddr)
    image_extensions = [".jpg", ".jpeg", ".png"]
    # need to convert unicode -> string apparently... (checked with print type(resource.servername))
    conn = SMBConnection(str(resource.userid), str(resource.password), client_machine_name, str(resource.servername),
                         use_ntlm_v2=True)
    assert conn.connect(server_ip, 139)

    file_obj = tempfile.NamedTemporaryFile()
    file_attributes, filesize = conn.retrieveFile(resource.sharename, image, file_obj)

    file_obj.seek(0)
    image_binary = file_obj.read()

    file_obj.close()

    return send_file(io.BytesIO(image_binary))