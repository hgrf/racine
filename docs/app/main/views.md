# Views

[Msm Index](../../README.md#msm-index) /
[App](../index.md#app) /
[Main](./index.md#main) /
Views

> Auto-generated documentation for [app.main.views](https://github.com/HolgerGraef/MSM/blob/main/app/main/views.py) module.

#### Attributes

- `supported_targets` - define supported fields: `{'sample': {'dbobject': Sample, 'auth': 'owner', 'fields': {'name': lambda x,: validate_form_field(NewSampleForm(), 'newsamplename', x), 'description': str, 'image': str}}, 'action': {'dbobject': Action, 'auth': 'action_auth', 'fields': {'timestamp': lambda x,: datetime.strptime(x, '%Y-%m-%d'), 'description': str}}, 'share': {'dbobject': Share, 'auth': None, 'fields': {}}, 'smbresource': {'dbobject': SMBResource, 'auth': 'admin', 'fields': {'name': str, 'servername': str, 'serveraddr': str, 'sharename': str, 'path': str, 'userid': str, 'password': str}}, 'user': {'dbobject': User, 'auth': 'admin', 'fields': {'username': lambda x,: validate_form_field(NewUserForm(), 'username', x), 'email': lambda x,: validate_form_field(NewUserForm(), 'email', x), 'is_admin': validate_is_admin}}}`


- [Views](#views)
  - [changeparent](#changeparent)
  - [createshare](#createshare)
  - [deleteaction](#deleteaction)
  - [deletesample](#deletesample)
  - [deleteshare](#deleteshare)
  - [editor](#editor)
  - [getfield](#getfield)
  - [help](#help)
  - [index](#index)
  - [login_as](#login_as)
  - [markasnews](#markasnews)
  - [navbar](#navbar)
  - [newaction](#newaction)
  - [newsample](#newsample)
  - [search](#search)
  - [static_file](#static_file)
  - [str_to_bool](#str_to_bool)
  - [swapactionorder](#swapactionorder)
  - [togglearchived](#togglearchived)
  - [togglecollaborative](#togglecollaborative)
  - [unmarkasnews](#unmarkasnews)
  - [updatefield](#updatefield)
  - [userlist](#userlist)
  - [validate_is_admin](#validate_is_admin)
  - [welcome](#welcome)

## changeparent

[Show source in views.py:379](https://github.com/HolgerGraef/MSM/blob/main/app/main/views.py#L379)

#### Signature

```python
@main.route("/changeparent", methods=["POST"])
@login_required
def changeparent():
    ...
```



## createshare

[Show source in views.py:289](https://github.com/HolgerGraef/MSM/blob/main/app/main/views.py#L289)

#### Signature

```python
@main.route("/createshare", methods=["POST"])
@login_required
def createshare():
    ...
```



## deleteaction

[Show source in views.py:321](https://github.com/HolgerGraef/MSM/blob/main/app/main/views.py#L321)

#### Signature

```python
@main.route("/delaction/<actionid>", methods=["GET", "POST"])
@login_required
def deleteaction(actionid):
    ...
```



## deletesample

[Show source in views.py:334](https://github.com/HolgerGraef/MSM/blob/main/app/main/views.py#L334)

#### Signature

```python
@main.route("/delsample/<sampleid>", methods=["GET", "POST"])
@login_required
def deletesample(sampleid):
    ...
```



## deleteshare

[Show source in views.py:347](https://github.com/HolgerGraef/MSM/blob/main/app/main/views.py#L347)

#### Signature

```python
@main.route("/delshare/<shareid>", methods=["GET", "POST"])
@login_required
def deleteshare(shareid):
    ...
```



## editor

[Show source in views.py:120](https://github.com/HolgerGraef/MSM/blob/main/app/main/views.py#L120)

#### Signature

```python
@main.route("/editor/<sampleid>", methods=["GET", "POST"])
@login_required
def editor(sampleid):
    ...
```



## getfield

[Show source in views.py:615](https://github.com/HolgerGraef/MSM/blob/main/app/main/views.py#L615)

#### Signature

```python
@main.route("/get/<target>/<field>/<id>", methods=["GET"])
@login_required
def getfield(target, field, id):
    ...
```



## help

[Show source in views.py:153](https://github.com/HolgerGraef/MSM/blob/main/app/main/views.py#L153)

#### Signature

```python
@main.route("/help")
@login_required
def help():
    ...
```



## index

[Show source in views.py:18](https://github.com/HolgerGraef/MSM/blob/main/app/main/views.py#L18)

#### Signature

```python
@main.route("/")
@main.route("/sample/<sampleid>")
def index(sampleid=0):
    ...
```



## login_as

[Show source in views.py:252](https://github.com/HolgerGraef/MSM/blob/main/app/main/views.py#L252)

#### Signature

```python
@main.route("/loginas", methods=["GET"])
@login_required
def login_as():
    ...
```



## markasnews

[Show source in views.py:448](https://github.com/HolgerGraef/MSM/blob/main/app/main/views.py#L448)

#### Signature

```python
@main.route("/markasnews", methods=["POST"])
@login_required
def markasnews():
    ...
```



## navbar

[Show source in views.py:104](https://github.com/HolgerGraef/MSM/blob/main/app/main/views.py#L104)

#### Signature

```python
@main.route("/navbar", methods=["GET"])
@login_required
def navbar():
    ...
```



## newaction

[Show source in views.py:502](https://github.com/HolgerGraef/MSM/blob/main/app/main/views.py#L502)

#### Signature

```python
@main.route("/newaction/<sampleid>", methods=["POST"])
@login_required
def newaction(sampleid):
    ...
```



## newsample

[Show source in views.py:427](https://github.com/HolgerGraef/MSM/blob/main/app/main/views.py#L427)

#### Signature

```python
@main.route("/newsample", methods=["POST"])
@login_required
def newsample():
    ...
```



## search

[Show source in views.py:160](https://github.com/HolgerGraef/MSM/blob/main/app/main/views.py#L160)

#### Signature

```python
@main.route("/search", methods=["GET"])
@login_required
def search():
    ...
```



## static_file

[Show source in views.py:540](https://github.com/HolgerGraef/MSM/blob/main/app/main/views.py#L540)

#### Signature

```python
@main.route("/plugins/<path:path>")
@login_required
def static_file(path):
    ...
```



## str_to_bool

[Show source in views.py:547](https://github.com/HolgerGraef/MSM/blob/main/app/main/views.py#L547)

#### Signature

```python
def str_to_bool(str):
    ...
```



## swapactionorder

[Show source in views.py:528](https://github.com/HolgerGraef/MSM/blob/main/app/main/views.py#L528)

#### Signature

```python
@main.route("/swapactionorder", methods=["POST"])
@login_required
def swapactionorder():
    ...
```



## togglearchived

[Show source in views.py:267](https://github.com/HolgerGraef/MSM/blob/main/app/main/views.py#L267)

#### Signature

```python
@main.route("/togglearchived", methods=["POST"])
@login_required
def togglearchived():
    ...
```



## togglecollaborative

[Show source in views.py:278](https://github.com/HolgerGraef/MSM/blob/main/app/main/views.py#L278)

#### Signature

```python
@main.route("/togglecollaborative", methods=["POST"])
@login_required
def togglecollaborative():
    ...
```



## unmarkasnews

[Show source in views.py:478](https://github.com/HolgerGraef/MSM/blob/main/app/main/views.py#L478)

#### Signature

```python
@main.route("/unmarkasnews", methods=["POST"])
@login_required
def unmarkasnews():
    ...
```



## updatefield

[Show source in views.py:644](https://github.com/HolgerGraef/MSM/blob/main/app/main/views.py#L644)

#### Signature

```python
@main.route("/set/<target>/<field>/<id>", methods=["POST"])
@login_required
def updatefield(target, field, id):
    ...
```



## userlist

[Show source in views.py:202](https://github.com/HolgerGraef/MSM/blob/main/app/main/views.py#L202)

#### Signature

```python
@main.route("/userlist", methods=["POST"])
@login_required
def userlist():
    ...
```



## validate_is_admin

[Show source in views.py:556](https://github.com/HolgerGraef/MSM/blob/main/app/main/views.py#L556)

#### Signature

```python
def validate_is_admin(str, item):
    ...
```



## welcome

[Show source in views.py:33](https://github.com/HolgerGraef/MSM/blob/main/app/main/views.py#L33)

#### Signature

```python
@main.route("/welcome")
@login_required
def welcome():
    ...
```


