# Views

[Msm Index](../../README.md#msm-index) /
[App](../index.md#app) /
[Settings](./index.md#settings) /
Views

> Auto-generated documentation for [app.settings.views](https://github.com/HolgerGraef/MSM/blob/main/app/settings/views.py) module.

- [Views](#views)
  - [email](#email)
  - [handle_img](#handle_img)
  - [handle_img_tags](#handle_img_tags)
  - [log](#log)
  - [revision](#revision)
  - [set_overview](#set_overview)
  - [smbresources](#smbresources)
  - [uploads](#uploads)
  - [users](#users)

## email

[Show source in views.py:67](https://github.com/HolgerGraef/MSM/blob/main/app/settings/views.py#L67)

#### Signature

```python
@settings.route("/email", methods=["GET", "POST"])
@login_required
@admin_required
def email():
    ...
```



## handle_img

[Show source in views.py:154](https://github.com/HolgerGraef/MSM/blob/main/app/settings/views.py#L154)

#### Signature

```python
def handle_img(loc, src, refdlist):
    ...
```



## handle_img_tags

[Show source in views.py:165](https://github.com/HolgerGraef/MSM/blob/main/app/settings/views.py#L165)

#### Signature

```python
def handle_img_tags(text, itemid, refdlist):
    ...
```



## log

[Show source in views.py:237](https://github.com/HolgerGraef/MSM/blob/main/app/settings/views.py#L237)

#### Signature

```python
@settings.route("/log", methods=["GET"])
@login_required
@admin_required
def log():
    ...
```



## revision

[Show source in views.py:114](https://github.com/HolgerGraef/MSM/blob/main/app/settings/views.py#L114)

#### Signature

```python
@settings.route("/revision", methods=["GET"])
@login_required
@admin_required
def revision():
    ...
```



## set_overview

[Show source in views.py:17](https://github.com/HolgerGraef/MSM/blob/main/app/settings/views.py#L17)

#### Signature

```python
@settings.route("/overview")
@login_required
@admin_required
def set_overview():
    ...
```



## smbresources

[Show source in views.py:24](https://github.com/HolgerGraef/MSM/blob/main/app/settings/views.py#L24)

#### Signature

```python
@settings.route("/smbresources", methods=["GET", "POST"])
@login_required
@admin_required
def smbresources():
    ...
```



## uploads

[Show source in views.py:181](https://github.com/HolgerGraef/MSM/blob/main/app/settings/views.py#L181)

#### Signature

```python
@settings.route("/uploads", methods=["GET"])
@login_required
@admin_required
def uploads():
    ...
```



## users

[Show source in views.py:49](https://github.com/HolgerGraef/MSM/blob/main/app/settings/views.py#L49)

#### Signature

```python
@settings.route("/users", methods=["GET", "POST"])
@login_required
@admin_required
def users():
    ...
```


