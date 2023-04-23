from flask import render_template, send_file, request, send_from_directory, jsonify
from flask_login import current_user, login_required
from flask import current_app as app
from .. import db
from ..models import SMBResource, Sample, Upload, Activity, ActivityType, record_activity
import os
from . import browser
import io
import hashlib
from xml.etree import ElementTree as ElementTree
from .. import smbinterface
from PIL import Image

IMAGE_EXTENSIONS = set([".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".svg"])
CONVERSION_REQUIRED = set([".tif", ".tiff"])
THUMBNAIL_SIZE = [120, 120]
PREVIEW_SIZE = [800, 800]

####################################################################################################
# Classes that contain the file/folder or resource info for easy transfer to the template
####################################################################################################


class FileTile:
    name = ""
    ext = ""
    image = ""
    path = ""


####################################################################################################
# Helper functions
####################################################################################################


def check_stored_file(upload):
    """Checks file size and SHA-256 hash for an upload and looks for duplicates in the database.

    If a duplicate is found, delete this upload and return the duplicate.

    NB: this means that if we upload two attachments with identical content but different names,
    the downloaded file will have the name of the first uploaded file

    This is separate from the store_file function, because store_file is specific to images right
    now and we might want to use the duplicate check for other file types, too (in the future).

    Parameters
    ----------
    upload : Upload

    Returns
    -------
    upload : Upload
        The upload or its duplicate.
    """

    # read file name from database
    filename = os.path.join(app.config["UPLOAD_FOLDER"], str(upload.id) + "." + upload.ext)
    # check file size and store in database entry
    upload.size = os.stat(filename).st_size
    # calculate SHA-256 hash for file and store in DB entry
    file_obj = open(filename, "rb")
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
    """Stores a file in the upload database and saves it in the upload folder,
    checking for duplicates.

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

    if type not in ("img", "att"):
        return None, "Invalid upload type."

    # create upload entry in database (in case upload fails, have to remove it later)
    upload = Upload(user=current_user, source=source, ext=ext[1:])  # use extension without the dot
    db.session.add(upload)
    db.session.commit()

    # save the file
    # TODO: if anything goes wrong here, we should delete the reference in the upload database again
    # check if the file_obj has a save method (flask uploads have it, pillow images have it,
    # but the file_obj from the smb_interface does not, so we have to save the file "manually")
    uploadpath = os.path.join(app.config["UPLOAD_FOLDER"], str(upload.id) + "." + upload.ext)
    if hasattr(file_obj, "save"):
        file_obj.save(uploadpath)
    else:
        with open(uploadpath, "wb") as f:
            f.write(file_obj.read())

    # calculate filesize, SHA-256 hash and check for duplicates
    upload = check_stored_file(upload)

    # make url for this upload
    uploadurl = "/browser/ul" + type + "/" + str(upload.id)

    return upload, uploadurl


def make_preview(upload, image):
    path = os.path.join(app.config["UPLOAD_FOLDER"], str(upload.id) + ".preview.jpg")
    if os.path.exists(path):
        raise Exception("Preview already exists.")

    # compress the image to JPG format and preview size
    # convert to RGB to remove alpha channel from PNG or BMP files
    if image.mode == "RGBA":
        # remove transparency by placing on white background
        background = Image.new("RGB", image.size, (255, 255, 255))
        background.paste(image, mask=image.split()[3])  # 3 is the alpha channel
        image = background
    image.thumbnail(PREVIEW_SIZE)
    # store the preview image
    image.convert("RGB").save(path)  # default quality for JPEG according to pillow doc is 75


def make_rotated(upload, angle, fullsize):
    ext = "." + upload.ext if fullsize else ".preview.jpg"
    rot_file = str(upload.id) + ".rot{}".format(angle) + ext
    rot_path = os.path.join(app.config["UPLOAD_FOLDER"], rot_file)

    # check if a rotated version already exists
    if os.path.exists(rot_path):
        return rot_file

    # try to rotate the image
    try:
        file_obj = open(os.path.join(app.config["UPLOAD_FOLDER"], str(upload.id) + ext), "rb")
        image = Image.open(file_obj)
        image.rotate(-angle, expand=True).save(rot_path)
        file_obj.close()
        return rot_file
    except Exception:
        return None


def store_image(file_obj, source, ext):
    """Stores an image file in the upload database and saves it in the upload folder,
    checking for duplicates.

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
    if ext not in IMAGE_EXTENSIONS:
        return (
            None,
            "File extension is invalid. Supported extensions are: " + ", ".join(IMAGE_EXTENSIONS),
            None,
        )

    # hack for SVG files (since we cannot open them with PIL)
    # see also:
    # https://stackoverflow.com/questions/24316032/can-pil-be-used-to-get-dimensions-of-an-svg-file
    # https://graphicdesign.stackexchange.com/questions/71568/is-there-any-concept-of-size-in-an-svg
    # http://osgeo-org.1560.x6.nabble.com/Get-size-of-SVG-in-Python-td5273032.html
    if ext == ".svg":
        def_dims = (800, 600)
        try:
            tree = ElementTree.parse(file_obj)
            attrib = tree.getroot().attrib
            if "height" in attrib and "width" in attrib:
                width = attrib["width"]
                height = attrib["height"]
                # remove unit (mm...) from these values

                width, height = strip_unit(width), strip_unit(height)
                height = int(height / width * 800)
                width = 800
            else:
                width, height = def_dims
        except Exception:
            width, height = def_dims
        file_obj.seek(0)  # return to beginning of file after parsing

        return store_file(file_obj, source, ext, "img") + ((width, height),)

    # check if image can be opened and if needs to be converted
    try:
        image = Image.open(file_obj)
        if ext in CONVERSION_REQUIRED:
            ext = ".png"
    except IOError:
        return None, "Image file invalid.", None

    # store image in original resolution
    upload, address = store_file(image, source, ext, "img")

    # make a preview image
    try:
        make_preview(upload, image)
    except Exception:
        # for now we ignore the exceptions, since even if no preview can be generated,
        # Racine will still serve the fullsize image instead
        pass

    return upload, address, (image.width, image.height)


# TODO: implement this for SMB? (right now not possible, because no support for normal file object)
def store_attachment(file_obj, source, ext):
    """Stores an image file in the upload database and saves it in the upload folder,
    checking for duplicates.

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

    return store_file(file_obj, source, ext, "att")


####################################################################################################
# View functions
####################################################################################################


@browser.route("/ulimg/<upload_id>", methods=["GET", "POST"])
@login_required
def retrieve_image(upload_id):
    """Retrieves an image that was uploaded to the server,

    either by uploading through the browser or by transfer from a SMB resource. The POST request is
    used by the CKEditor plugin imagerotate to retrieve potential error messages.

    Parameters
    ----------
    upload_id : int
        The ID of the image to be retrieved, corresponding to a row in the uploads database table.
    """

    # TODO: check that user has right to view the image (this might be tricky because the sample
    #       might be a shared one)

    def retrieve_image_error(message):
        if request.method == "GET":
            return render_template("errors/404.html"), 404
        else:
            return jsonify(code=1, message=message)

    # determine rotation angle and fullsize from query parameters
    if request.args.get("rot") is None:
        rot = 0
    else:
        try:
            rot = int(request.args.get("rot"))
        except Exception:
            return retrieve_image_error("Could not parse angle")
    if rot not in [0, 90, 180, 270]:
        return retrieve_image_error("Invalid rotation angle")
    fullsize = "fullsize" in request.args

    # find the upload in the database
    dbentry = Upload.query.get(upload_id)
    if dbentry is None:
        return retrieve_image_error("File not found.")

    # cannot get a rotated version of SVG images
    if dbentry.ext == "svg" and rot:
        return retrieve_image_error("SVG images cannot be rotated.")

    # rotate if requested
    if rot:
        rot_file = make_rotated(dbentry, rot, fullsize)
        if rot_file:
            return send_from_directory(app.config["UPLOAD_FOLDER"], rot_file)
        else:
            return retrieve_image_error("Failed to rotate image.")

    # otherwise return original image
    if fullsize:
        return send_from_directory(app.config["UPLOAD_FOLDER"], str(dbentry.id) + "." + dbentry.ext)
    else:
        # check if preview exists, otherwise send full size
        if os.path.exists(
            os.path.join(app.config["UPLOAD_FOLDER"], str(dbentry.id) + ".preview.jpg")
        ):
            return send_from_directory(
                app.config["UPLOAD_FOLDER"], str(dbentry.id) + ".preview.jpg"
            )
        else:
            return send_from_directory(
                app.config["UPLOAD_FOLDER"], str(dbentry.id) + "." + dbentry.ext
            )


@browser.route("/ulatt/<upload_id>")
@login_required
def retrieve_attachment(upload_id):
    """Retrieves an attachment that was uploaded to the server.

    Parameters
    ----------
    upload_id : int
        The ID of the attachment to be retrieved, corresponding to a row in the
        uploads database table.
    """

    # TODO: check that user has right to view the attachment

    dbentry = Upload.query.get(upload_id)
    if dbentry is not None:
        srctype, src = dbentry.source.split(":", 1)
        if srctype == "ul":
            att_filename = src
        elif srctype == "smb":
            att_filename = os.path.basename(src)
        else:
            att_filename = "unknown." + dbentry.ext
        if dbentry.ext.lower() == "pdf":
            response = send_from_directory(
                app.config["UPLOAD_FOLDER"],
                str(dbentry.id) + "." + dbentry.ext,
                as_attachment=False,
            )
            response.headers["Content-Disposition"] = "inline; filename={}".format(att_filename)
            return response
        else:
            return send_from_directory(
                app.config["UPLOAD_FOLDER"],
                str(dbentry.id) + "." + dbentry.ext,
                as_attachment=True,
                download_name=att_filename,
            )
    else:
        return render_template("errors/404.html"), 404


@browser.route("/smbimg/<path:path>")
@login_required
def retrieve_smb_image(path):
    """Retrieves an image from a SMB resource. This is only for the browser, so we will send
    back thumbnails to speed up the communication a bit.

    Parameters
    ----------
    path : str
        The path to the image, consisting of the name of the SMB resource and the address
        within the resource.
    """

    # get a file object for the requested path and try to open it with PIL
    # TODO: error handling for get_file
    file_obj = smbinterface.get_file(path)

    # check if it's an SVG file (in this case we won't create a thumbnail)
    if os.path.splitext(path)[1].lower() == ".svg":
        return send_file(file_obj, mimetype="image/svg+xml")

    # open the image for thumbnail creation
    try:
        image = Image.open(file_obj)

        # TODO: very similar code in make_preview(), create a function for this
        # compress the image to JPG format and preview size
        # convert to RGB to remove alpha channel from PNG or BMP files
        if image.mode == "RGBA":
            # remove transparency by placing on white background
            background = Image.new("RGB", image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[3])  # 3 is the alpha channel
            image = background

        # convert the image to a thumbnail and store it in thumbnail JPEG format in memory
        # before sending it to user
        image.thumbnail(THUMBNAIL_SIZE)
        image_binary = io.BytesIO()
        image.convert("RGB").save(image_binary, "JPEG")
        image.close()
        image_binary.seek(0)  # need to go back to beginning of stream
        return send_file(image_binary, mimetype="image/jpeg")
    except Exception:
        return send_file(os.path.join(app.config["RACINE_FOLDER"], "app/static/images/file.png"))


@browser.route("/", defaults={"smb_path": ""})
@browser.route("/<path:smb_path>")
@login_required
def imagebrowser(smb_path):
    # get last locations from activity log:
    atype = ActivityType.query.filter_by(description="selectsmbfile").first()
    # get the last 20 selectsmbfile events from the activity table
    browser_history = [
        act.description[: act.description.rfind("/")]
        for act in Activity.query.filter_by(type_id=atype.id, user_id=current_user.id)
        .order_by(Activity.id.desc())
        .limit(20)
        .all()
    ]
    # remove duplicates and limit to 5 elements
    # NB: here I assume that in the 20 elements selected above the user has
    # at least 5 different locations
    seen = set()
    browser_history = [x for x in browser_history if not (x in seen or seen.add(x))]
    browser_history = browser_history[:5]

    # process address
    smb_path = smb_path.strip("/")  # this is necessary for Internet Explorer when going to xxx/..
    resource, path_on_server = smbinterface.process_smb_path(smb_path)

    if resource is None:
        # list resources
        return render_template(
            "browser.html", resources=SMBResource.query.all(), browser_history=browser_history
        )
    else:
        # list files and folders in current path
        files = []
        folders = []
        try:
            listpath = smbinterface.list_path(smb_path)
        except Exception:
            return render_template(
                "browser.html",
                error=True,
                message="Folder could not be found on server: " + smb_path,
            )
        if listpath is None:
            return render_template(
                "browser.html", error=True, message="Could not connect to server: " + smb_path
            )
        for item in listpath:
            # ignore . entry
            if item.filename == ".":
                continue
            f = FileTile()
            f.name, f.ext = os.path.splitext(item.filename)
            if not item.isDirectory:
                f.path = smb_path + ("" if smb_path == "" else "/") + f.name + f.ext
                if f.ext.lower() in IMAGE_EXTENSIONS:
                    f.image = "/browser/smbimg/" + f.path
                else:
                    f.image = "/static/images/file.png"
                files.append(f)
            else:
                f.image = "/static/images/folder.png"
                folders.append(f)

        # sort by name and return
        files = sorted(files, key=lambda f: f.name.lower())
        folders = sorted(folders, key=lambda f: f.name.lower())
        return render_template(
            "browser.html", error=False, files=files, folders=folders, smb_path=smb_path
        )


@browser.route("/upload", methods=["POST"])
@login_required
def uploadfile():
    # find out what kind of upload we are dealing with and who sent it
    type = request.args.get("type")
    if type is None or type not in ("img", "att"):
        return "error"

    file_obj = request.files["upload"]
    filename, ext = os.path.splitext(file_obj.filename)

    if type == "img":
        upload, url, dimensions = store_image(file_obj, "ul:" + file_obj.filename, ext)
    else:
        upload, url = store_attachment(file_obj, "ul:" + file_obj.filename, ext)

    uploaded = 0 if upload is None else 1
    message = "" if uploaded else url

    if type == "img":
        return jsonify(
            uploaded=uploaded,
            filename=filename + ext,
            url=url,
            error={"message": message},
            width=400,
            height=int(float(dimensions[1]) / float(dimensions[0]) * 400.0) if uploaded else 0,
        )
    else:
        return jsonify(
            uploaded=uploaded, filename=filename + ext, url=url, error={"message": message}
        )


@browser.route("/savefromsmb", methods=["POST"])
@login_required
def save_from_smb():
    path = request.form.get("path")
    type = request.form.get("type")

    # check if path is provided
    if path is None:
        return jsonify(code=1, message="No path specified.")

    # check if type is valid
    if type is None or type not in ("img", "att", "auto"):
        return jsonify(code=1, message="Invalid type.")

    ext = os.path.splitext(path)[1]

    # get a file object for the requested path
    file_obj = smbinterface.get_file(path)
    if not file_obj:
        return jsonify(
            code=1,
            message="File could not be retrieved from SMB resource.",
            filename=os.path.basename(path),
        )

    # store the file
    if type == "img":
        upload, uploadurl, dimensions = store_image(file_obj, "smb:" + path, ext)
    elif type == "att":
        upload, uploadurl = store_attachment(file_obj, "smb:" + path, ext)
    else:
        # automatically determine if file is stored as image or as attachment
        type = "img"
        upload, uploadurl, dimensions = store_image(file_obj, "smb:" + path, ext)
        if upload is None:
            type = "att"
            upload, uploadurl = store_attachment(file_obj, "smb:" + path, ext)

    # record activity
    record_activity("selectsmbfile", current_user, description=path, commit=True)

    if upload is not None:
        return jsonify(code=0, uploadurl=uploadurl, filename=os.path.basename(path), type=type)
    else:
        return jsonify(code=1, message=uploadurl, filename=os.path.basename(path))


@browser.route("/inspectpath", methods=["POST"])
@login_required
def inspectpath():
    # TODO: smbinterface.list_path should clearly communicate why it could not list the path,
    # the following is more of a workaround
    try:
        listpath = smbinterface.list_path(request.form.get("smbpath"))
        if listpath is None:
            return jsonify(code=1, error="noconnection")
        else:
            return jsonify(code=0)
    except Exception:
        return jsonify(code=1, error="notfound")


@browser.route("/inspectresource", methods=["POST"])
@login_required
def inspectresource():
    # if sample ID is provided, look up sample
    if request.form.get("sampleid") is not None:
        sample = Sample.query.get(request.form.get("sampleid"))
    else:
        sample = None

    resource = SMBResource.query.get(request.form.get("resourceid"))
    if resource is None:
        return jsonify(code=1, resourceid=request.form.get("resourceid"))

    # we want to display a shortcut either to the current user's or to the
    # sample owner's folder in the resource
    user = sample.owner if sample is not None else current_user

    # initialise attributes to return
    userfolder = ""
    samplefolder = ""

    listpath = smbinterface.list_path(resource.name)
    if listpath is None:
        return jsonify(code=2, resourceid=resource.id)  # resource not available / connection failed
    for item in listpath:
        if item.isDirectory and item.filename == user.username:
            userfolder = resource.name + "/" + item.filename
            # if a sample is given, let's browse this folder for a sample folder
            if sample is not None:
                listsubpath = smbinterface.list_path(userfolder)
                if listsubpath is None:
                    # something went wrong with resource, we can connect,
                    # but maybe we have no right to access the userfolder
                    return jsonify(code=0, resourceid=resource.id, userfolder="", samplefolder="")
                for subitem in listsubpath:
                    if subitem.isDirectory and subitem.filename == sample.name:
                        samplefolder = userfolder + "/" + subitem.filename
                        break
            break

    return jsonify(code=0, resourceid=resource.id, userfolder=userfolder, samplefolder=samplefolder)


def strip_unit(s):
    numeric = "0123456789-."
    for i, c in enumerate(s):
        if c not in numeric:
            break
    return float(s[:i])
