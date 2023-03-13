# Views

[Racine Index](../../README.md#racine-index) /
[App](../index.md#app) /
[Main](./index.md#main) /
Views

> Auto-generated documentation for [app.main.views](https://github.com/hgrf/racine/blob/master/app/main/views.py) module.

#### Attributes

- `supported_targets` - define supported fields: `{'sample': {'dbobject': Sample, 'auth': 'owner', 'fields': {'name': lambda x,: validate_form_field(NewSampleForm(), 'newsamplename', x), 'description': str, 'image': str}}, 'action': {'dbobject': Action, 'auth': 'action_auth', 'fields': {'timestamp': lambda x,: datetime.strptime(x, '%Y-%m-%d'), 'description': str}}, 'share': {'dbobject': Share, 'auth': None, 'fields': {}}, 'smbresource': {'dbobject': SMBResource, 'auth': 'admin', 'fields': {'name': str, 'servername': str, 'serveraddr': str, 'sharename': str, 'path': str, 'userid': str, 'password': str}}, 'user': {'dbobject': User, 'auth': 'admin', 'fields': {'username': lambda x,: validate_form_field(NewUserForm(), 'username', x), 'email': lambda x,: validate_form_field(NewUserForm(), 'email', x), 'is_admin': validate_is_admin}}}`


## changeparent

[Show source in views.py:486](https://github.com/hgrf/racine/blob/master/app/main/views.py#L486)

#### Signature

```python
@main.route("/changeparent", methods=["POST"])
@login_required
def changeparent():
    ...
```



## createshare

[Show source in views.py:391](https://github.com/hgrf/racine/blob/master/app/main/views.py#L391)

#### Signature

```python
@main.route("/createshare", methods=["POST"])
@login_required
def createshare():
    ...
```



## deleteaction

[Show source in views.py:428](https://github.com/hgrf/racine/blob/master/app/main/views.py#L428)

#### Signature

```python
@main.route("/delaction/<actionid>", methods=["GET", "POST"])
@login_required
def deleteaction(actionid):
    ...
```



## deletesample

[Show source in views.py:441](https://github.com/hgrf/racine/blob/master/app/main/views.py#L441)

#### Signature

```python
@main.route("/delsample/<sampleid>", methods=["GET", "POST"])
@login_required
def deletesample(sampleid):
    ...
```



## deleteshare

[Show source in views.py:454](https://github.com/hgrf/racine/blob/master/app/main/views.py#L454)

#### Signature

```python
@main.route("/delshare/<shareid>", methods=["GET", "POST"])
@login_required
def deleteshare(shareid):
    ...
```



## editor

[Show source in views.py:186](https://github.com/hgrf/racine/blob/master/app/main/views.py#L186)

#### Signature

```python
@main.route("/editor/<sampleid>", methods=["GET", "POST"])
@login_required
def editor(sampleid):
    ...
```



## getfield

[Show source in views.py:751](https://github.com/hgrf/racine/blob/master/app/main/views.py#L751)

#### Signature

```python
@main.route("/get/<target>/<field>/<id>", methods=["GET"])
@login_required
def getfield(target, field, id):
    ...
```



## help

[Show source in views.py:232](https://github.com/hgrf/racine/blob/master/app/main/views.py#L232)

#### Signature

```python
@main.route("/help")
@login_required
def help():
    ...
```



## index

[Show source in views.py:29](https://github.com/hgrf/racine/blob/master/app/main/views.py#L29)

#### Signature

```python
@main.route("/")
@main.route("/sample/<sampleid>")
def index(sampleid=0):
    ...
```



## login_as

[Show source in views.py:350](https://github.com/hgrf/racine/blob/master/app/main/views.py#L350)

#### Signature

```python
@main.route("/loginas", methods=["GET"])
@login_required
def login_as():
    ...
```



## markasnews

[Show source in views.py:568](https://github.com/hgrf/racine/blob/master/app/main/views.py#L568)

#### Signature

```python
@main.route("/markasnews", methods=["POST"])
@login_required
def markasnews():
    ...
```



## navbar

[Show source in views.py:161](https://github.com/hgrf/racine/blob/master/app/main/views.py#L161)

#### Signature

```python
@main.route("/navbar", methods=["GET"])
@login_required
def navbar():
    ...
```



## newaction

[Show source in views.py:634](https://github.com/hgrf/racine/blob/master/app/main/views.py#L634)

#### Signature

```python
@main.route("/newaction/<sampleid>", methods=["POST"])
@login_required
def newaction(sampleid):
    ...
```



## newsample

[Show source in views.py:541](https://github.com/hgrf/racine/blob/master/app/main/views.py#L541)

#### Signature

```python
@main.route("/newsample", methods=["POST"])
@login_required
def newsample():
    ...
```



## search

[Show source in views.py:239](https://github.com/hgrf/racine/blob/master/app/main/views.py#L239)

#### Signature

```python
@main.route("/search", methods=["GET"])
@login_required
def search():
    ...
```



## static_file

[Show source in views.py:679](https://github.com/hgrf/racine/blob/master/app/main/views.py#L679)

#### Signature

```python
@main.route("/plugins/<path:path>")
@login_required
def static_file(path):
    ...
```



## str_to_bool

[Show source in views.py:689](https://github.com/hgrf/racine/blob/master/app/main/views.py#L689)

#### Signature

```python
def str_to_bool(str):
    ...
```



## swapactionorder

[Show source in views.py:667](https://github.com/hgrf/racine/blob/master/app/main/views.py#L667)

#### Signature

```python
@main.route("/swapactionorder", methods=["POST"])
@login_required
def swapactionorder():
    ...
```



## togglearchived

[Show source in views.py:365](https://github.com/hgrf/racine/blob/master/app/main/views.py#L365)

#### Signature

```python
@main.route("/togglearchived", methods=["POST"])
@login_required
def togglearchived():
    ...
```



## togglecollaborative

[Show source in views.py:378](https://github.com/hgrf/racine/blob/master/app/main/views.py#L378)

#### Signature

```python
@main.route("/togglecollaborative", methods=["POST"])
@login_required
def togglecollaborative():
    ...
```



## unmarkasnews

[Show source in views.py:604](https://github.com/hgrf/racine/blob/master/app/main/views.py#L604)

#### Signature

```python
@main.route("/unmarkasnews", methods=["POST"])
@login_required
def unmarkasnews():
    ...
```



## updatefield

[Show source in views.py:782](https://github.com/hgrf/racine/blob/master/app/main/views.py#L782)

#### Signature

```python
@main.route("/set/<target>/<field>/<id>", methods=["POST"])
@login_required
def updatefield(target, field, id):
    ...
```



## userlist

[Show source in views.py:292](https://github.com/hgrf/racine/blob/master/app/main/views.py#L292)

#### Signature

```python
@main.route("/userlist", methods=["POST"])
@login_required
def userlist():
    ...
```



## validate_is_admin

[Show source in views.py:698](https://github.com/hgrf/racine/blob/master/app/main/views.py#L698)

#### Signature

```python
def validate_is_admin(str, item):
    ...
```



## welcome

[Show source in views.py:56](https://github.com/hgrf/racine/blob/master/app/main/views.py#L56)

#### Signature

```python
@main.route("/welcome")
@login_required
def welcome():
    ...
```