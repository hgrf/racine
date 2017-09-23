from flask import render_template, send_file, request, redirect, url_for, send_from_directory, jsonify, abort
from flask_login import current_user, login_required
from flask import current_app as app
from .. import db
from ..models import SMBResource, Sample, Upload
import os
from . import browser
import io
import hashlib
from .. import smbinterface
from PIL import Image

ALLOWED_EXTENSIONS = set(['.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff'])
CONVERSION_REQUIRED = set(['.tif', '.tiff'])

########################################################################################################################
# Notes
########################################################################################################################
"""Possible scenarios:
1) Browser was opened from CKEditor
    In this case we always need to provide the browser with the callback number for the CKEditor.
    1.1) Browser was opened from CKEditor in action editor
        In this case we know which sample we are dealing with, so we can use it to find the sample folder within
        SMB resources.
    1.2) Browser was opened from CKEditor in new sample description editor
        In this case we have no sample information for now.
2) Browser was opened from editor page in order to find a new sample image.
    In this case we have no callback function, but the browser will need to update the sample image when it is
    closed.
    
In order to make sure that the JavaScript part knows the sample ID and the CKEditorFuncNum, we need to make sure that
these are always in the query string. This is taken care of by the JavaScript part.
"""

########################################################################################################################
# Classes that contain the file/folder or resource info for easy transfer to the template
########################################################################################################################

class FileTile:
    name = ""
    ext = ""
    image = ""


class ResourceTile:
    name = ""
    available = True        # set to false if connection to resource cannot be established
    hasuserfolder = False
    hassamplefolder = False


########################################################################################################################
# Helper functions
########################################################################################################################

def check_stored_file(upload):
    """Checks file size and SHA-256 hash for an upload and looks for duplicates in the database.

    If a duplicate is found, delete this upload and return the duplicate.

    This is separate from the store_file function, because store_file is specific to images right now and
    we might want to use the duplicate check for other file types, too (in the future).

    Parameters
    ----------
    upload : Upload

    Returns
    -------
    upload : Upload
        The upload or its duplicate.
    """

    # read file name from database
    filename = os.path.join(app.config['UPLOAD_FOLDER'], str(upload.id) + '.' + upload.ext)
    # check file size and store in database entry
    upload.size = os.stat(filename).st_size
    # calculate SHA-256 hash for file and store in DB entry
    file_obj = open(filename, 'rb')
    upload.hash = hashlib.sha256(file_obj.read()).hexdigest()
    db.session.commit()
    file_obj.close()

    # check if upload already exists
    identicals = Upload.query.filter_by(hash=upload.hash).all()
    for i in identicals:
        if i.id != upload.id:
            # found different upload with same hash, need to delete file that was just uploaded and
            # also the corresponding database entry
            os.remove(filename)
            db.session.delete(upload)
            db.session.commit()
            return i

    return upload


# TODO: rename this to store_image (to distinguish from the store_file we will have later for attachments)
def store_file(file_obj, source, ext):
    """Stores an image file in the upload database and saves it in the upload folder, checking for duplicates.

    Parameters
    ----------
    file_obj : file object
    source : str
    ext : str

    Returns
    -------
    upload : Upload object or None
    message : str
        upload URL if upload succeeds or error message if it fails
    """

    # check if file is OK and if extension is allowed
    ext = ext.lower()

    if not file_obj:
        return None, "File could not be read."
    if not ext in ALLOWED_EXTENSIONS:
        return None, "File extension is invalid."

    # check if image can be opened and if needs to be converted
    try:
        image = Image.open(file_obj)
        if ext in CONVERSION_REQUIRED:
            ext = '.png'
    except IOError:
        return None, "Image file invalid."

    # create upload entry in database (in case upload fails, have to remove it later)
    upload = Upload(user=current_user, source=source, ext=ext)
    db.session.add(upload)
    db.session.commit()

    # save the file
    # TODO: if anything goes wrong here, we should delete the reference in the upload database again
    image.save(os.path.join(app.config['UPLOAD_FOLDER'], str(upload.id) + '.' + upload.ext))

    # calculate filesize, SHA-256 hash and check for duplicates
    upload = check_stored_file(upload)

    # make url for this upload
    uploadurl = url_for('.retrieve_image', image=str(upload.id))

    return upload, uploadurl

def make_resource_list(sample):
    """Makes a list of resource tiles by iterating through all of the available SMB resources.

    Checks for every resource if it is online and if user/sample folders can be found.

    Parameters
    ----------
    sample : Sample or None

    Returns
    -------
    resources
    """
    resources = SMBResource.query.all()
    for i,resource in enumerate(resources):
        r = ResourceTile()
        r.name = resource.name
        r.available = True

        # TODO: error handling for listpath and check what happens when it gets empty list
        listpath = smbinterface.list_path(r.name)
        if listpath:
            # find user/sample folders
            for item in listpath:
                if item.isDirectory and item.filename == (sample.owner.username if sample is not None else current_user.username):
                    r.hasuserfolder = True
                    for subitem in smbinterface.list_path(resource.name+'/'+item.filename):
                        if subitem.isDirectory and sample is not None and subitem.filename == sample.name:
                            r.hassamplefolder = True
                            break
                    break
        else:
            r.available = False
            r.name += " (N/A)"

        resources[i] = r        # replace SQL row by ResourceTile

    return resources


########################################################################################################################
# View functions
########################################################################################################################

@browser.route('/ulimg/<image>')
@login_required
def retrieve_image(image):
    """Retrieves an image that was uploaded to the server,

    either by uploading through the browser or by transfer from a SMB resource.

    Parameters
    ----------
    image : int
        The ID of the image to be retrieved, corresponding to a row in the uploads database table.
    """

    # TODO: check that user has right to view the image (this might be tricky because the sample might be a shared one)

    dbentry = Upload.query.filter_by(id=image).first()
    return send_from_directory(app.config['UPLOAD_FOLDER'], str(dbentry.id)+'.'+dbentry.ext)


@browser.route('/smbimg/<path:path>')
@login_required
def retrieve_smb_image(path):
    """Retrieves an image from a SMB resource. This is only for the browser, so we will send back thumbnails to speed
    up the communication a bit.

    Parameters
    ----------
    path : str
        The path to the image, consisting of the name of the SMB resource and the address within the resource.
    """

    # get a file object for the requested path and try to open it with PIL
    # TODO: error handling for get_file
    file_obj = smbinterface.get_file(path)
    try:
        image = Image.open(file_obj)
    except IOError:
        abort(500)

    # convert the image to a thumbnail and store it in thumbnail JPEG format in memory before sending it to user
    image_binary = io.BytesIO()
    image.thumbnail([140, 140])
    image.save(image_binary, 'JPEG')
    image.close()
    image_binary.seek(0)        # need to go back to beginning of stream
    return send_file(image_binary)


def render_browser_root(**kwargs):
    # find out from which sample the browser was opened
    if request.args.get("sample") is None:
        sample = None
    else:
        sample = Sample.query.filter_by(id=int(request.args.get("sample"))).first()

    # in the browser root we will show the file upload field and a list of available SMB resources
    return render_template('browser.html', resources=make_resource_list(sample), sample=sample,
                           owner=sample.owner if sample is not None else current_user, **kwargs)


@browser.route('/', defaults={'address': ''})
@browser.route('/<path:address>')
@login_required
def imagebrowser(address):
    # process address
    resource, path_on_server = smbinterface.process_smb_path(address)

    if resource is None:
        return render_browser_root()
    else:
        # list files and folders in current path
        files = []
        folders = []
        listpath = smbinterface.list_path(address)
        # TODO: error handling for list path
        for i in listpath:
            if i.filename == '.':
                continue
            f = FileTile()
            f.name, f.ext = os.path.splitext(i.filename)
            if not i.isDirectory:
                if f.ext.lower() in ALLOWED_EXTENSIONS:
                    f.image = "/browser/smbimg/" + address + (
                        "" if address == "" else "/") + f.name + f.ext  # will at some point cause problems with big image files, consider caching compressed icons
                else:
                    f.image = "/static/file.png"
                files.append(f)
            else:
                f.image = "/static/folder.png"
                folders.append(f)

        files = sorted(files, key=lambda f: f.name)
        folders = sorted(folders, key=lambda f: f.name)
        return render_template('browser.html', files=files, folders=folders, address=address)


@browser.route('/upload', methods=['POST'])
@login_required
def uploadfile():
    file_obj = request.files['file']
    filename, ext = os.path.splitext(file_obj.filename)

    # store the file
    upload, uploadurl = store_file(file_obj, 'ul:'+file_obj.filename, ext)

    if upload is not None:
        # notify of successful upload
        return render_template('browser.html', uploadurl=uploadurl)
    else:
        # render browser root and notify of failed upload
        return render_browser_root(uploadfailed=True, errormessage=uploadurl, extensions=', '.join(ALLOWED_EXTENSIONS))


@browser.route('/savefromsmb', methods=['POST'])
@login_required
def savefromsmb():
    # get img src string for the image (i.e. this will include the '/browser/img/' path)
    src = request.form.get('src')

    # get rid of '/browser/img/', if it's not there return error
    if not src[:16] == '/browser/smbimg/':
        return jsonify(code=1, message="File has to be in /browser/smbimg sub-path.")
    path = src[16:]
    pathwithoutext, ext = os.path.splitext(path)

    # get a file object for the requested path
    file_obj = smbinterface.get_file(path)
    if not file_obj:
        return jsonify(code=1, message="File could not be retrieved from SMB resource.")

    # store the file
    upload, uploadurl = store_file(file_obj, 'smb:'+src, ext)

    if upload is not None:
        return jsonify(code=0, uploadurl=uploadurl)
    else:
        return jsonify(code=1, message=uploadurl)
