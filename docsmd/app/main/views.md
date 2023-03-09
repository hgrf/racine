# Views

[Racine Index](../../README.md#racine-index) /
[App](../index.md#app) /
[Main](./index.md#main) /
Views

> Auto-generated documentation for [app.main.views](https://github.com/hgrf/racine/blob/master/app/main/views.py) module.

#### Attributes

- `supported_targets` - define supported fields: `{'sample': {'dbobject': Sample, 'auth': 'owner', 'fields': {'name': lambda x,: validate_form_field(NewSampleForm(), 'newsamplename', x), 'description': str, 'image': str}}, 'action': {'dbobject': Action, 'auth': 'action_auth', 'fields': {'timestamp': lambda x,: datetime.strptime(x, '%Y-%m-%d'), 'description': str}}, 'share': {'dbobject': Share, 'auth': None, 'fields': {}}, 'smbresource': {'dbobject': SMBResource, 'auth': 'admin', 'fields': {'name': str, 'servername': str, 'serveraddr': str, 'sharename': str, 'path': str, 'userid': str, 'password': str}}, 'user': {'dbobject': User, 'auth': 'admin', 'fields': {'username': lambda x,: validate_form_field(NewUserForm(), 'username', x), 'email': lambda x,: validate_form_field(NewUserForm(), 'email', x), 'is_admin': validate_is_admin}}}`


## changeparent

[Show source in views.py:485](https://github.com/hgrf/racine/blob/master/app/main/views.py#L485)

#### Signature

```python
@main.route("/changeparent", methods=["POST"])
@login_required
def changeparent():
    ...
```



## createshare

[Show source in views.py:390](https://github.com/hgrf/racine/blob/master/app/main/views.py#L390)

#### Signature

```python
@main.route("/createshare", methods=["POST"])
@login_required
def createshare():
    ...
```



## deleteaction

[Show source in views.py:427](https://github.com/hgrf/racine/blob/master/app/main/views.py#L427)

#### Signature

```python
@main.route("/delaction/<actionid>", methods=["GET", "POST"])
@login_required
def deleteaction(actionid):
    ...
```



## deletesample

[Show source in views.py:440](https://github.com/hgrf/racine/blob/master/app/main/views.py#L440)

#### Signature

```python
@main.route("/delsample/<sampleid>", methods=["GET", "POST"])
@login_required
def deletesample(sampleid):
    ...
```



## deleteshare

[Show source in views.py:453](https://github.com/hgrf/racine/blob/master/app/main/views.py#L453)

#### Signature

```python
@main.route("/delshare/<shareid>", methods=["GET", "POST"])
@login_required
def deleteshare(shareid):
    ...
```



## editor

[Show source in views.py:185](https://github.com/hgrf/racine/blob/master/app/main/views.py#L185)

#### Signature

```python
@main.route("/editor/<sampleid>", methods=["GET", "POST"])
@login_required
def editor(sampleid):
    ...
```



## getfield

[Show source in views.py:747](https://github.com/hgrf/racine/blob/master/app/main/views.py#L747)

#### Signature

```python
@main.route("/get/<target>/<field>/<id>", methods=["GET"])
@login_required
def getfield(target, field, id):
    ...
```



## help

[Show source in views.py:231](https://github.com/hgrf/racine/blob/master/app/main/views.py#L231)

#### Signature

```python
@main.route("/help")
@login_required
def help():
    ...
```



## index

[Show source in views.py:28](https://github.com/hgrf/racine/blob/master/app/main/views.py#L28)

#### Signature

```python
@main.route("/")
@main.route("/sample/<sampleid>")
def index(sampleid=0):
    ...
```



## login_as

[Show source in views.py:349](https://github.com/hgrf/racine/blob/master/app/main/views.py#L349)

#### Signature

```python
@main.route("/loginas", methods=["GET"])
@login_required
def login_as():
    ...
```



## markasnews

[Show source in views.py:567](https://github.com/hgrf/racine/blob/master/app/main/views.py#L567)

#### Signature

```python
@main.route("/markasnews", methods=["POST"])
@login_required
def markasnews():
    ...
```



## navbar

[Show source in views.py:160](https://github.com/hgrf/racine/blob/master/app/main/views.py#L160)

#### Signature

```python
@main.route("/navbar", methods=["GET"])
@login_required
def navbar():
    ...
```



## newaction

[Show source in views.py:633](https://github.com/hgrf/racine/blob/master/app/main/views.py#L633)

#### Signature

```python
@main.route("/newaction/<sampleid>", methods=["POST"])
@login_required
def newaction(sampleid):
    ...
```



## newsample

[Show source in views.py:540](https://github.com/hgrf/racine/blob/master/app/main/views.py#L540)

#### Signature

```python
@main.route("/newsample", methods=["POST"])
@login_required
def newsample():
    ...
```



## search

[Show source in views.py:238](https://github.com/hgrf/racine/blob/master/app/main/views.py#L238)

#### Signature

```python
@main.route("/search", methods=["GET"])
@login_required
def search():
    ...
```



## static_file

[Show source in views.py:678](https://github.com/hgrf/racine/blob/master/app/main/views.py#L678)

#### Signature

```python
@main.route("/plugins/<path:path>")
@login_required
def static_file(path):
    ...
```



## str_to_bool

[Show source in views.py:685](https://github.com/hgrf/racine/blob/master/app/main/views.py#L685)

#### Signature

```python
def str_to_bool(str):
    ...
```



## swapactionorder

[Show source in views.py:666](https://github.com/hgrf/racine/blob/master/app/main/views.py#L666)

#### Signature

```python
@main.route("/swapactionorder", methods=["POST"])
@login_required
def swapactionorder():
    ...
```



## togglearchived

[Show source in views.py:364](https://github.com/hgrf/racine/blob/master/app/main/views.py#L364)

#### Signature

```python
@main.route("/togglearchived", methods=["POST"])
@login_required
def togglearchived():
    ...
```



## togglecollaborative

[Show source in views.py:377](https://github.com/hgrf/racine/blob/master/app/main/views.py#L377)

#### Signature

```python
@main.route("/togglecollaborative", methods=["POST"])
@login_required
def togglecollaborative():
    ...
```



## unmarkasnews

[Show source in views.py:603](https://github.com/hgrf/racine/blob/master/app/main/views.py#L603)

#### Signature

```python
@main.route("/unmarkasnews", methods=["POST"])
@login_required
def unmarkasnews():
    ...
```



## updatefield

[Show source in views.py:778](https://github.com/hgrf/racine/blob/master/app/main/views.py#L778)

#### Signature

```python
@main.route("/set/<target>/<field>/<id>", methods=["POST"])
@login_required
def updatefield(target, field, id):
    ...
```



## userlist

[Show source in views.py:291](https://github.com/hgrf/racine/blob/master/app/main/views.py#L291)

#### Signature

```python
@main.route("/userlist", methods=["POST"])
@login_required
def userlist():
    ...
```



## validate_is_admin

[Show source in views.py:694](https://github.com/hgrf/racine/blob/master/app/main/views.py#L694)

#### Signature

```python
def validate_is_admin(str, item):
    ...
```



## welcome

[Show source in views.py:55](https://github.com/hgrf/racine/blob/master/app/main/views.py#L55)

#### Signature

```python
@main.route("/welcome")
@login_required
def welcome():
    ...
```
