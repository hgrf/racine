# Views

[Racine Index](../../README.md#racine-index) /
[App](../index.md#app) /
[Profile](./index.md#profile) /
Views

> Auto-generated documentation for [app.profile.views](https://github.com/hgrf/racine/blob/master/app/profile/views.py) module.

## changedetails

[Show source in views.py:9](https://github.com/hgrf/racine/blob/master/app/profile/views.py#L9)

#### Signature

```python
@profile.route("/changedetails", methods=["GET", "POST"])
@login_required
def changedetails():
    ...
```



## changepassword

[Show source in views.py:26](https://github.com/hgrf/racine/blob/master/app/profile/views.py#L26)

#### Signature

```python
@profile.route("/changepassword", methods=["GET", "POST"])
@login_required
def changepassword():
    ...
```



## leave

[Show source in views.py:41](https://github.com/hgrf/racine/blob/master/app/profile/views.py#L41)

#### Signature

```python
@profile.route("/leave", methods=["GET"])
@login_required
def leave():
    ...
```
