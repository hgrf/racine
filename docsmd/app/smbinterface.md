# SMBInterface

[Racine Index](../README.md#racine-index) /
[App](./index.md#app) /
SMBInterface

> Auto-generated documentation for [app.smbinterface](https://github.com/hgrf/racine/blob/master/app/smbinterface.py) module.

## SMBInterface

[Show source in smbinterface.py:8](https://github.com/hgrf/racine/blob/master/app/smbinterface.py#L8)

#### Signature

```python
class SMBInterface:
    def __init__(self):
        ...
```

### SMBInterface().get_file

[Show source in smbinterface.py:14](https://github.com/hgrf/racine/blob/master/app/smbinterface.py#L14)

Creates a temporary file object and reads the content of a remote SMB file into it.

Parameters
----------
path : str
    The path pointing to the SMB resource and location within the resource.

Returns
-------
file : file object
    A file object.

#### Signature

```python
def get_file(self, path):
    ...
```

### SMBInterface().list_path

[Show source in smbinterface.py:53](https://github.com/hgrf/racine/blob/master/app/smbinterface.py#L53)

#### Signature

```python
def list_path(self, path):
    ...
```

### SMBInterface().process_smb_path

[Show source in smbinterface.py:73](https://github.com/hgrf/racine/blob/master/app/smbinterface.py#L73)

Splits up the SMB path of type "/ResourceName/path_in_resource".

The path in the resource is not necessarily the same as the path on the server, because a resource can already
point to a subdirectory on the server. If the path is empty, this function will return None, ''. The same will
be returned if the requested resource does not exist.

Parameters
----------
path: str

Returns
-------
resource : SMBResource
path_on_server : str

#### Signature

```python
def process_smb_path(self, path):
    ...
```
