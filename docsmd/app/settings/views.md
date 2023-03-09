# Views

[Racine Index](../../README.md#racine-index) /
[App](../index.md#app) /
[Settings](./index.md#settings) /
Views

> Auto-generated documentation for [app.settings.views](https://github.com/hgrf/racine/blob/master/app/settings/views.py) module.

## email

[Show source in views.py:82](https://github.com/hgrf/racine/blob/master/app/settings/views.py#L82)

#### Signature

```python
@settings.route("/email", methods=["GET", "POST"])
@login_required
@admin_required
def email():
    ...
```



## handle_img

[Show source in views.py:184](https://github.com/hgrf/racine/blob/master/app/settings/views.py#L184)

#### Signature

```python
def handle_img(loc, src, refdlist):
    ...
```



## handle_img_tags

[Show source in views.py:196](https://github.com/hgrf/racine/blob/master/app/settings/views.py#L196)

#### Signature

```python
def handle_img_tags(text, itemid, refdlist):
    ...
```



## log

[Show source in views.py:278](https://github.com/hgrf/racine/blob/master/app/settings/views.py#L278)

#### Signature

```python
@settings.route("/log", methods=["GET"])
@login_required
@admin_required
def log():
    ...
```



## revision

[Show source in views.py:138](https://github.com/hgrf/racine/blob/master/app/settings/views.py#L138)

#### Signature

```python
@settings.route("/revision", methods=["GET"])
@login_required
@admin_required
def revision():
    ...
```



## set_overview

[Show source in views.py:17](https://github.com/hgrf/racine/blob/master/app/settings/views.py#L17)

#### Signature

```python
@settings.route("/overview")
@login_required
@admin_required
def set_overview():
    ...
```



## smbresources

[Show source in views.py:24](https://github.com/hgrf/racine/blob/master/app/settings/views.py#L24)

#### Signature

```python
@settings.route("/smbresources", methods=["GET", "POST"])
@login_required
@admin_required
def smbresources():
    ...
```



## uploads

[Show source in views.py:213](https://github.com/hgrf/racine/blob/master/app/settings/views.py#L213)

#### Signature

```python
@settings.route("/uploads", methods=["GET"])
@login_required
@admin_required
def uploads():
    ...
```



## users

[Show source in views.py:59](https://github.com/hgrf/racine/blob/master/app/settings/views.py#L59)

#### Signature

```python
@settings.route("/users", methods=["GET", "POST"])
@login_required
@admin_required
def users():
    ...
```
