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

IMAGE_EXTENSIONS = set(['.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff'])
CONVERSION_REQUIRED = set(['.tif', '.tiff'])
THUMBNAIL_SIZE = [120, 120]

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


def store_file(file_obj, source, ext, type):
    """Stores a file in the upload database and saves it in the upload folder, checking for duplicates.

    Parameters
    ----------
    file_obj : FileStorage or Image object, or any other object with save() function
    source : str
    ext : str
    type : str
        'img' or 'att'

    Returns
    -------
    upload : Upload object or None
    message : str
        upload URL if upload succeeds or error message if it fails
    """

    if type not in ('img', 'att'):
        return None, "Invalid upload type."

    # create upload entry in database (in case upload fails, have to remove it later)
    upload = Upload(user=current_user, source=source, ext=ext[1:])  # use extension without the dot
    db.session.add(upload)
    db.session.commit()

    # save the file
    # TODO: if anything goes wrong here, we should delete the reference in the upload database again
    file_obj.save(os.path.join(app.config['UPLOAD_FOLDER'], str(upload.id) + '.' + upload.ext))

    # calculate filesize, SHA-256 hash and check for duplicates
    upload = check_stored_file(upload)

    # make url for this upload
    uploadurl = '/browser/ul'+type+'/'+str(upload.id)

    return upload, uploadurl


def store_image(file_obj, source, ext):
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
    dimensions : tuple
        (width, height) of the image
    """

    # check if file is OK and if extension is allowed
    ext = ext.lower()

    if not file_obj:
        return None, "File could not be read.", None
    if not ext in IMAGE_EXTENSIONS:
        return None, "File extension is invalid.", None

    # check if image can be opened and if needs to be converted
    try:
        image = Image.open(file_obj)
        if ext in CONVERSION_REQUIRED:
            ext = '.png'
    except IOError:
        return None, "Image file invalid.", None

    return store_file(image, source, ext, 'img')+((image.width, image.height),)


# TODO: implement this for SMB? (right now not possible, because no support for normal file object)
def store_attachment(file_obj, source, ext):
    """Stores an image file in the upload database and saves it in the upload folder, checking for duplicates.

    Parameters
    ----------
    file_obj : FileStorage object or any other object with save() function
    source : str
    ext : str

    Returns
    -------
    upload : Upload object or None
    message : str
        upload URL if upload succeeds or error message if it fails
    """

    return store_file(file_obj, source, ext, 'att')

########################################################################################################################
# View functions
########################################################################################################################

@browser.route('/ulimg/<upload_id>')
@login_required
def retrieve_image(upload_id):
    """Retrieves an image that was uploaded to the server,

    either by uploading through the browser or by transfer from a SMB resource.

    Parameters
    ----------
    upload_id : int
        The ID of the image to be retrieved, corresponding to a row in the uploads database table.
    """

    # TODO: check that user has right to view the image (this might be tricky because the sample might be a shared one)

    dbentry = Upload.query.get(upload_id)
    if dbentry is not None:
        return send_from_directory(app.config['UPLOAD_FOLDER'], str(dbentry.id)+'.'+dbentry.ext)
    else:
        return render_template('404.html'), 404


@browser.route('/ulatt/<upload_id>')
@login_required
def retrieve_attachment(upload_id):
    """Retrieves an attachment that was uploaded to the server.

    Parameters
    ----------
    upload_id : int
        The ID of the attachment to be retrieved, corresponding to a row in the uploads database table.
    """

    # TODO: check that user has right to view the attachment

    dbentry = Upload.query.get(upload_id)
    if dbentry is not None:
        return send_from_directory(app.config['UPLOAD_FOLDER'], str(dbentry.id)+'.'+dbentry.ext,
                                   as_attachment=True, attachment_filename=dbentry.source[3:])
    else:
        return render_template('404.html'), 404


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
    image.thumbnail(THUMBNAIL_SIZE)
    image.save(image_binary, 'JPEG')
    image.close()
    image_binary.seek(0)        # need to go back to beginning of stream
    return send_file(image_binary)


@browser.route('/', defaults={'smb_path': ''})
@browser.route('/<path:smb_path>')
@login_required
def imagebrowser(smb_path):
    # process address
    resource, path_on_server = smbinterface.process_smb_path(smb_path)

    if resource is None:
        # list resources
        return render_template('browser.html', resources=SMBResource.query.all())
    else:
        # list files and folders in current path
        files = []
        folders = []
        listpath = smbinterface.list_path(smb_path)
        if listpath is None:
            abort(500)
        for item in listpath:
            # ignore . entry
            if item.filename == '.':
                continue
            f = FileTile()
            f.name, f.ext = os.path.splitext(item.filename)
            if not item.isDirectory:
                if f.ext.lower() in IMAGE_EXTENSIONS:
                    f.image = '/browser/smbimg/' + smb_path + ('' if smb_path == '' else '/') + f.name + f.ext
                else:
                    f.image = "/static/images/file.png"
                files.append(f)
            else:
                f.image = "/static/images/folder.png"
                folders.append(f)

        # sort by name and return
        files = sorted(files, key=lambda f: f.name.lower())
        folders = sorted(folders, key=lambda f: f.name.lower())
        return render_template('browser.html', files=files, folders=folders, smb_path=smb_path)


@browser.route('/upload', methods=['POST'])
@login_required
def uploadfile():
    # find out what kind of upload we are dealing with and who sent it
    type = request.args.get('type')
    caller = request.args.get('caller')
    if type is None or not type in ('img', 'att') or caller is None or not caller in ('ckb', 'ckdd', 'msmb'):
        return 'error'

    # caller meaning:
    #  ckb = CKEditor "browser"
    #  ckdd = CKEditor drag/drop or copy/paste
    #  msmb = MSM browser (normally to change sample image)

    file_obj = request.files['upload']
    filename, ext = os.path.splitext(file_obj.filename)

    if type == 'img':
        upload, url, dimensions = store_image(file_obj, 'ul:'+file_obj.filename, ext)
    else:
        upload, url = store_attachment(file_obj, 'ul:' + file_obj.filename, ext)

    uploaded = 0 if upload is None else 1
    message = '' if uploaded else url

    if caller == 'ckdd' or caller == 'ckb':
        if type == 'img':
            return jsonify(uploaded=uploaded, filename=filename+ext, url=url, message=message, width=400,
                           height=int(float(dimensions[1])/float(dimensions[0])*400.))
        else:
            return jsonify(uploaded=uploaded, filename=filename+ext, url=url, message=message)

    if caller == 'msmb':
        if upload is not None:
            # notify of successful upload
            return render_template('browser.html', uploadurl=url)
        else:
            # render browser root and notify of failed upload
            return render_template('browser.html', resources=SMBResource.query.all(),
                                   uploadfailed=True, errormessage=message, extensions=", ".join(IMAGE_EXTENSIONS))


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
    upload, uploadurl, dimensions = store_image(file_obj, 'smb:'+src, ext)

    if upload is not None:
        return jsonify(code=0, uploadurl=uploadurl)
    else:
        return jsonify(code=1, message=uploadurl)


@browser.route('/inspectresource', methods=['POST'])
@login_required
def inspectresource():
    # if sample ID is provided, look up sample
    if request.form.get('sampleid') is not None:
        sample = Sample.query.get(request.form.get('sampleid'))
    else:
        sample = None

    resource = SMBResource.query.get(request.form.get('resourceid'))
    if resource is None:
        return jsonify(code=1, resourceid=request.form.get('resourceid'))

    # we want to display a shortcut either to the current user's or to the sample owner's folder in the resource
    user = sample.owner if sample is not None else current_user

    # initialise attributes to return
    userfolder = ''
    samplefolder = ''

    listpath = smbinterface.list_path(resource.name)
    if listpath is None:
        return jsonify(code=2, resourceid=resource.id)  # resource not available / connection failed
    for item in listpath:
        if item.isDirectory and item.filename == user.username:
            userfolder = resource.name+'/'+item.filename
            # if a sample is given, let's browse this folder for a sample folder
            if sample is not None:
                listsubpath = smbinterface.list_path(userfolder)
                if listsubpath is None:
                    # something went wrong with resource, we can connect,
                    # but maybe we have no right to access the userfolder
                    return jsonify(code=0, resourceid=resource.id, userfolder='', samplefolder='')
                for subitem in listsubpath:
                    if subitem.isDirectory and subitem.filename == sample.name:
                        samplefolder = userfolder+'/'+subitem.filename
                        break
            break

    return jsonify(code=0, resourceid=resource.id, userfolder=userfolder, samplefolder=samplefolder)