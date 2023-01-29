# Views

[Mercury Sample Manager Index](../../README.md#mercury-sample-manager-index) /
[App](../index.md#app) /
[Main](./index.md#main) /
Views

> Auto-generated documentation for [app.main.views](https://github.com/HolgerGraef/MSM/blob/master/app/main/views.py) module.

#### Attributes

- `supported_targets` - define supported fields: `{'sample': {'dbobject': Sample, 'auth': 'owner', 'fields': {'name': lambda x,: validate_form_field(NewSampleForm(), 'newsamplename', x), 'description': str, 'image': str}}, 'action': {'dbobject': Action, 'auth': 'action_auth', 'fields': {'timestamp': lambda x,: datetime.strptime(x, '%Y-%m-%d'), 'description': str}}, 'share': {'dbobject': Share, 'auth': None, 'fields': {}}, 'smbresource': {'dbobject': SMBResource, 'auth': 'admin', 'fields': {'name': str, 'servername': str, 'serveraddr': str, 'sharename': str, 'path': str, 'userid': str, 'password': str}}, 'user': {'dbobject': User, 'auth': 'admin', 'fields': {'username': lambda x,: validate_form_field(NewUserForm(), 'username', x), 'email': lambda x,: validate_form_field(NewUserForm(), 'email', x), 'is_admin': validate_is_admin}}}`


## changeparent

[Show source in views.py:484](https://github.com/HolgerGraef/MSM/blob/master/app/main/views.py#L484)

#### Signature

```python
@main.route("/changeparent", methods=["POST"])
@login_required
def changeparent():
    ...
```



## createshare

[Show source in views.py:389](https://github.com/HolgerGraef/MSM/blob/master/app/main/views.py#L389)

#### Signature

```python
@main.route("/createshare", methods=["POST"])
@login_required
def createshare():
    ...
```



## deleteaction

[Show source in views.py:426](https://github.com/HolgerGraef/MSM/blob/master/app/main/views.py#L426)

#### Signature

```python
@main.route("/delaction/<actionid>", methods=["GET", "POST"])
@login_required
def deleteaction(actionid):
    ...
```



## deletesample

[Show source in views.py:439](https://github.com/HolgerGraef/MSM/blob/master/app/main/views.py#L439)

#### Signature

```python
@main.route("/delsample/<sampleid>", methods=["GET", "POST"])
@login_required
def deletesample(sampleid):
    ...
```



## deleteshare

[Show source in views.py:452](https://github.com/HolgerGraef/MSM/blob/master/app/main/views.py#L452)

#### Signature

```python
@main.route("/delshare/<shareid>", methods=["GET", "POST"])
@login_required
def deleteshare(shareid):
    ...
```



## editor

[Show source in views.py:185](https://github.com/HolgerGraef/MSM/blob/master/app/main/views.py#L185)

#### Signature

```python
@main.route("/editor/<sampleid>", methods=["GET", "POST"])
@login_required
def editor(sampleid):
    ...
```



## getfield

[Show source in views.py:746](https://github.com/HolgerGraef/MSM/blob/master/app/main/views.py#L746)

#### Signature

```python
@main.route("/get/<target>/<field>/<id>", methods=["GET"])
@login_required
def getfield(target, field, id):
    ...
```



## help

[Show source in views.py:231](https://github.com/HolgerGraef/MSM/blob/master/app/main/views.py#L231)

#### Signature

```python
@main.route("/help")
@login_required
def help():
    ...
```



## index

[Show source in views.py:28](https://github.com/HolgerGraef/MSM/blob/master/app/main/views.py#L28)

#### Signature

```python
@main.route("/")
@main.route("/sample/<sampleid>")
def index(sampleid=0):
    ...
```



## login_as

[Show source in views.py:348](https://github.com/HolgerGraef/MSM/blob/master/app/main/views.py#L348)

#### Signature

```python
@main.route("/loginas", methods=["GET"])
@login_required
def login_as():
    ...
```



## markasnews

[Show source in views.py:566](https://github.com/HolgerGraef/MSM/blob/master/app/main/views.py#L566)

#### Signature

```python
@main.route("/markasnews", methods=["POST"])
@login_required
def markasnews():
    ...
```



## navbar

[Show source in views.py:160](https://github.com/HolgerGraef/MSM/blob/master/app/main/views.py#L160)

#### Signature

```python
@main.route("/navbar", methods=["GET"])
@login_required
def navbar():
    ...
```



## newaction

[Show source in views.py:632](https://github.com/HolgerGraef/MSM/blob/master/app/main/views.py#L632)

#### Signature

```python
@main.route("/newaction/<sampleid>", methods=["POST"])
@login_required
def newaction(sampleid):
    ...
```



## newsample

[Show source in views.py:539](https://github.com/HolgerGraef/MSM/blob/master/app/main/views.py#L539)

#### Signature

```python
@main.route("/newsample", methods=["POST"])
@login_required
def newsample():
    ...
```



## search

[Show source in views.py:238](https://github.com/HolgerGraef/MSM/blob/master/app/main/views.py#L238)

#### Signature

```python
@main.route("/search", methods=["GET"])
@login_required
def search():
    ...
```



## static_file

[Show source in views.py:677](https://github.com/HolgerGraef/MSM/blob/master/app/main/views.py#L677)

#### Signature

```python
@main.route("/plugins/<path:path>")
@login_required
def static_file(path):
    ...
```



## str_to_bool

[Show source in views.py:684](https://github.com/HolgerGraef/MSM/blob/master/app/main/views.py#L684)

#### Signature

```python
def str_to_bool(str):
    ...
```



## swapactionorder

[Show source in views.py:665](https://github.com/HolgerGraef/MSM/blob/master/app/main/views.py#L665)

#### Signature

```python
@main.route("/swapactionorder", methods=["POST"])
@login_required
def swapactionorder():
    ...
```



## togglearchived

[Show source in views.py:363](https://github.com/HolgerGraef/MSM/blob/master/app/main/views.py#L363)

#### Signature

```python
@main.route("/togglearchived", methods=["POST"])
@login_required
def togglearchived():
    ...
```



## togglecollaborative

[Show source in views.py:376](https://github.com/HolgerGraef/MSM/blob/master/app/main/views.py#L376)

#### Signature

```python
@main.route("/togglecollaborative", methods=["POST"])
@login_required
def togglecollaborative():
    ...
```



## unmarkasnews

[Show source in views.py:602](https://github.com/HolgerGraef/MSM/blob/master/app/main/views.py#L602)

#### Signature

```python
@main.route("/unmarkasnews", methods=["POST"])
@login_required
def unmarkasnews():
    ...
```



## updatefield

[Show source in views.py:777](https://github.com/HolgerGraef/MSM/blob/master/app/main/views.py#L777)

#### Signature

```python
@main.route("/set/<target>/<field>/<id>", methods=["POST"])
@login_required
def updatefield(target, field, id):
    ...
```



## userlist

[Show source in views.py:290](https://github.com/HolgerGraef/MSM/blob/master/app/main/views.py#L290)

#### Signature

```python
@main.route("/userlist", methods=["POST"])
@login_required
def userlist():
    ...
```



## validate_is_admin

[Show source in views.py:693](https://github.com/HolgerGraef/MSM/blob/master/app/main/views.py#L693)

#### Signature

```python
def validate_is_admin(str, item):
    ...
```



## welcome

[Show source in views.py:55](https://github.com/HolgerGraef/MSM/blob/master/app/main/views.py#L55)

#### Signature

```python
@main.route("/welcome")
@login_required
def welcome():
    ...
```
