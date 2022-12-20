# Views

[Msm Index](../../README.md#msm-index) /
[App](../index.md#app) /
[Browser](./index.md#browser) /
Views

> Auto-generated documentation for [app.browser.views](https://github.com/HolgerGraef/MSM/blob/main/app/browser/views.py) module.

- [Views](#views)
  - [FileTile](#filetile)
  - [check_stored_file](#check_stored_file)
  - [imagebrowser](#imagebrowser)
  - [inspectpath](#inspectpath)
  - [inspectresource](#inspectresource)
  - [make_preview](#make_preview)
  - [make_rotated](#make_rotated)
  - [retrieve_attachment](#retrieve_attachment)
  - [retrieve_image](#retrieve_image)
  - [retrieve_smb_image](#retrieve_smb_image)
  - [save_from_smb](#save_from_smb)
  - [store_attachment](#store_attachment)
  - [store_file](#store_file)
  - [store_image](#store_image)
  - [strip_unit](#strip_unit)
  - [uploadfile](#uploadfile)

## FileTile

[Show source in views.py:23](https://github.com/HolgerGraef/MSM/blob/main/app/browser/views.py#L23)

#### Signature

```python
class FileTile:
    ...
```



## check_stored_file

[Show source in views.py:34](https://github.com/HolgerGraef/MSM/blob/main/app/browser/views.py#L34)

Checks file size and SHA-256 hash for an upload and looks for duplicates in the database.

If a duplicate is found, delete this upload and return the duplicate.

NB: this means that if we upload two attachments with identical content but different names,
the downloaded file will have the name of the first uploaded file

This is separate from the store_file function, because store_file is specific to images right now and
we might want to use the duplicate check for other file types, too (in the future).

Parameters
----------
upload : Upload

Returns
-------
upload : Upload
    The upload or its duplicate.

#### Signature

```python
def check_stored_file(upload):
    ...
```



## imagebrowser

[Show source in views.py:398](https://github.com/HolgerGraef/MSM/blob/main/app/browser/views.py#L398)

#### Signature

```python
@browser.route("/", defaults={"smb_path": ""})
@browser.route("/<path:smb_path>")
@login_required
def imagebrowser(smb_path):
    ...
```



## inspectpath

[Show source in views.py:529](https://github.com/HolgerGraef/MSM/blob/main/app/browser/views.py#L529)

#### Signature

```python
@browser.route("/inspectpath", methods=["POST"])
@login_required
def inspectpath():
    ...
```



## inspectresource

[Show source in views.py:544](https://github.com/HolgerGraef/MSM/blob/main/app/browser/views.py#L544)

#### Signature

```python
@browser.route("/inspectresource", methods=["POST"])
@login_required
def inspectresource():
    ...
```



## make_preview

[Show source in views.py:124](https://github.com/HolgerGraef/MSM/blob/main/app/browser/views.py#L124)

#### Signature

```python
def make_preview(upload, image):
    ...
```



## make_rotated

[Show source in views.py:141](https://github.com/HolgerGraef/MSM/blob/main/app/browser/views.py#L141)

#### Signature

```python
def make_rotated(upload, angle, fullsize):
    ...
```



## retrieve_attachment

[Show source in views.py:320](https://github.com/HolgerGraef/MSM/blob/main/app/browser/views.py#L320)

Retrieves an attachment that was uploaded to the server.

Parameters
----------
upload_id : int
    The ID of the attachment to be retrieved, corresponding to a row in the uploads database table.

#### Signature

```python
@browser.route("/ulatt/<upload_id>")
@login_required
def retrieve_attachment(upload_id):
    ...
```



## retrieve_image

[Show source in views.py:258](https://github.com/HolgerGraef/MSM/blob/main/app/browser/views.py#L258)

Retrieves an image that was uploaded to the server,

either by uploading through the browser or by transfer from a SMB resource. The POST request is used by the
CKEditor plugin imagerotate to retrieve potential error messages.

Parameters
----------
upload_id : int
    The ID of the image to be retrieved, corresponding to a row in the uploads database table.

#### Signature

```python
@browser.route("/ulimg/<upload_id>", methods=["GET", "POST"])
@login_required
def retrieve_image(upload_id):
    ...
```



## retrieve_smb_image

[Show source in views.py:354](https://github.com/HolgerGraef/MSM/blob/main/app/browser/views.py#L354)

Retrieves an image from a SMB resource. This is only for the browser, so we will send back thumbnails to speed
up the communication a bit.

Parameters
----------
path : str
    The path to the image, consisting of the name of the SMB resource and the address within the resource.

#### Signature

```python
@browser.route("/smbimg/<path:path>")
@login_required
def retrieve_smb_image(path):
    ...
```



## save_from_smb

[Show source in views.py:484](https://github.com/HolgerGraef/MSM/blob/main/app/browser/views.py#L484)

#### Signature

```python
@browser.route("/savefromsmb", methods=["POST"])
@login_required
def save_from_smb():
    ...
```



## store_attachment

[Show source in views.py:236](https://github.com/HolgerGraef/MSM/blob/main/app/browser/views.py#L236)

Stores an image file in the upload database and saves it in the upload folder, checking for duplicates.

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

#### Signature

```python
def store_attachment(file_obj, source, ext):
    ...
```



## store_file

[Show source in views.py:79](https://github.com/HolgerGraef/MSM/blob/main/app/browser/views.py#L79)

Stores a file in the upload database and saves it in the upload folder, checking for duplicates.

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

#### Signature

```python
def store_file(file_obj, source, ext, type):
    ...
```



## store_image

[Show source in views.py:161](https://github.com/HolgerGraef/MSM/blob/main/app/browser/views.py#L161)

Stores an image file in the upload database and saves it in the upload folder, checking for duplicates.

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

#### Signature

```python
def store_image(file_obj, source, ext):
    ...
```



## strip_unit

[Show source in views.py:586](https://github.com/HolgerGraef/MSM/blob/main/app/browser/views.py#L586)

#### Signature

```python
def strip_unit(s):
    ...
```



## uploadfile

[Show source in views.py:458](https://github.com/HolgerGraef/MSM/blob/main/app/browser/views.py#L458)

#### Signature

```python
@browser.route("/upload", methods=["POST"])
@login_required
def uploadfile():
    ...
```


