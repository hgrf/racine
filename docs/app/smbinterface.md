# SMBInterface

[Msm Index](../README.md#msm-index) /
[App](./index.md#app) /
SMBInterface

> Auto-generated documentation for [app.smbinterface](https://github.com/HolgerGraef/MSM/blob/main/app/smbinterface.py) module.

- [SMBInterface](#smbinterface)
  - [SMBInterface](#smbinterface-1)
    - [SMBInterface().get_file](#smbinterface()get_file)
    - [SMBInterface().list_path](#smbinterface()list_path)
    - [SMBInterface().process_smb_path](#smbinterface()process_smb_path)

## SMBInterface

[Show source in smbinterface.py:7](https://github.com/HolgerGraef/MSM/blob/main/app/smbinterface.py#L7)

#### Signature

```python
class SMBInterface:
    def __init__(self):
        ...
```

### SMBInterface().get_file

[Show source in smbinterface.py:13](https://github.com/HolgerGraef/MSM/blob/main/app/smbinterface.py#L13)

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

[Show source in smbinterface.py:50](https://github.com/HolgerGraef/MSM/blob/main/app/smbinterface.py#L50)

#### Signature

```python
def list_path(self, path):
    ...
```

### SMBInterface().process_smb_path

[Show source in smbinterface.py:70](https://github.com/HolgerGraef/MSM/blob/main/app/smbinterface.py#L70)

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


