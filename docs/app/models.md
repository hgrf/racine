# Models

[Msm Index](../README.md#msm-index) /
[App](./index.md#app) /
Models

> Auto-generated documentation for [app.models](https://github.com/HolgerGraef/MSM/blob/main/app/models.py) module.

- [Models](#models)
  - [Action](#action)
    - [Action().has_read_access](#action()has_read_access)
    - [Action().has_write_access](#action()has_write_access)
  - [Activity](#activity)
  - [ActivityType](#activitytype)
  - [LinkUserNews](#linkusernews)
  - [News](#news)
    - [News().dispatch](#news()dispatch)
    - [News().render_content](#news()render_content)
  - [SMBResource](#smbresource)
  - [Sample](#sample)
    - [Sample().is_accessible_for](#sample()is_accessible_for)
    - [Sample().logical_parent](#sample()logical_parent)
    - [Sample().mountedsamples](#sample()mountedsamples)
  - [Share](#share)
  - [Upload](#upload)
  - [User](#user)
    - [User().directshares](#user()directshares)
    - [User().generate_reset_token](#user()generate_reset_token)
    - [User().password](#user()password)
    - [User().password](#user()password-1)
    - [User.reset_password](#userreset_password)
    - [User().verify_password](#user()verify_password)
  - [after_flush](#after_flush)
  - [deleted_sample_handler](#deleted_sample_handler)
  - [deleted_share_handler](#deleted_share_handler)
  - [load_user](#load_user)
  - [record_activity](#record_activity)

## Action

[Show source in models.py:266](https://github.com/HolgerGraef/MSM/blob/main/app/models.py#L266)

#### Signature

```python
class Action(db.Model):
    ...
```

### Action().has_read_access

[Show source in models.py:282](https://github.com/HolgerGraef/MSM/blob/main/app/models.py#L282)

#### Signature

```python
def has_read_access(self, user):
    ...
```

### Action().has_write_access

[Show source in models.py:291](https://github.com/HolgerGraef/MSM/blob/main/app/models.py#L291)

#### Signature

```python
def has_write_access(self, user):
    ...
```



## Activity

[Show source in models.py:405](https://github.com/HolgerGraef/MSM/blob/main/app/models.py#L405)

#### Signature

```python
class Activity(db.Model):
    ...
```



## ActivityType

[Show source in models.py:423](https://github.com/HolgerGraef/MSM/blob/main/app/models.py#L423)

#### Signature

```python
class ActivityType(db.Model):
    ...
```



## LinkUserNews

[Show source in models.py:356](https://github.com/HolgerGraef/MSM/blob/main/app/models.py#L356)

#### Signature

```python
class LinkUserNews(db.Model):
    ...
```



## News

[Show source in models.py:295](https://github.com/HolgerGraef/MSM/blob/main/app/models.py#L295)

#### Attributes

- `recipient_id` - recipient can be either all users, a specific user, or all users who share a given sample: `db.Column(db.Integer, db.ForeignKey('users.id'))`

- `recipients` - action = db.relationship('Action', backref="news"): `db.relationship('LinkUserNews', backref='news', foreign_keys='LinkUserNews.news_id', cascade='delete')`


#### Signature

```python
class News(db.Model):
    ...
```

### News().dispatch

[Show source in models.py:314](https://github.com/HolgerGraef/MSM/blob/main/app/models.py#L314)

#### Signature

```python
def dispatch(self):
    ...
```

### News().render_content

[Show source in models.py:343](https://github.com/HolgerGraef/MSM/blob/main/app/models.py#L343)

#### Signature

```python
def render_content(self):
    ...
```



## SMBResource

[Show source in models.py:366](https://github.com/HolgerGraef/MSM/blob/main/app/models.py#L366)

#### Signature

```python
class SMBResource(db.Model):
    ...
```



## Sample

[Show source in models.py:166](https://github.com/HolgerGraef/MSM/blob/main/app/models.py#L166)

#### Attributes

- `iscollaborative` - in collaborative samples, all sharing users can edit all actions: `db.Column(db.Boolean)`

- `children` - NB: the cascade delete for shares and actions is no longer used because we delete samples by
  setting isdeleted to True: `db.relationship('Sample', backref=db.backref('parent', remote_side=[id]))`


#### Signature

```python
class Sample(db.Model):
    ...
```

### Sample().is_accessible_for

[Show source in models.py:209](https://github.com/HolgerGraef/MSM/blob/main/app/models.py#L209)

 go through the owner and shares of this sample and check in the hierarchy (i.e. all parents)
if it can be accessed by user

- if indirect_only is True, only look for indirect shares, i.e. parent shares
- if direct_only is True, only look for direct shares

indirect sharing has priority over direct sharing in order to avoid clogging up the hierarchy

#### Signature

```python
def is_accessible_for(self, user, indirect_only=False, direct_only=False):
    ...
```

### Sample().logical_parent

[Show source in models.py:248](https://github.com/HolgerGraef/MSM/blob/main/app/models.py#L248)

#### Signature

```python
@property
def logical_parent(self):
    ...
```

### Sample().mountedsamples

[Show source in models.py:238](https://github.com/HolgerGraef/MSM/blob/main/app/models.py#L238)

make a list of samples that are mounted in this one by the current user

#### Signature

```python
@property
def mountedsamples(self):
    ...
```



## Share

[Show source in models.py:381](https://github.com/HolgerGraef/MSM/blob/main/app/models.py#L381)

#### Signature

```python
class Share(db.Model):
    ...
```



## Upload

[Show source in models.py:392](https://github.com/HolgerGraef/MSM/blob/main/app/models.py#L392)

#### Signature

```python
class Upload(db.Model):
    ...
```



## User

[Show source in models.py:102](https://github.com/HolgerGraef/MSM/blob/main/app/models.py#L102)

#### Signature

```python
class User(UserMixin, db.Model):
    ...
```

### User().directshares

[Show source in models.py:150](https://github.com/HolgerGraef/MSM/blob/main/app/models.py#L150)

 determine the user's direct shares that are not mounted anywhere in his tree
(i.e. they are at the top level)

#### Signature

```python
@property
def directshares(self):
    ...
```

### User().generate_reset_token

[Show source in models.py:132](https://github.com/HolgerGraef/MSM/blob/main/app/models.py#L132)

#### Signature

```python
def generate_reset_token(self, expiration=3600):
    ...
```

### User().password

[Show source in models.py:121](https://github.com/HolgerGraef/MSM/blob/main/app/models.py#L121)

#### Signature

```python
@property
def password(self):
    ...
```

### User().password

[Show source in models.py:125](https://github.com/HolgerGraef/MSM/blob/main/app/models.py#L125)

#### Signature

```python
@password.setter
def password(self, password):
    ...
```

### User.reset_password

[Show source in models.py:136](https://github.com/HolgerGraef/MSM/blob/main/app/models.py#L136)

#### Signature

```python
@staticmethod
def reset_password(token, new_password):
    ...
```

### User().verify_password

[Show source in models.py:129](https://github.com/HolgerGraef/MSM/blob/main/app/models.py#L129)

#### Signature

```python
def verify_password(self, password):
    ...
```



## after_flush

[Show source in models.py:84](https://github.com/HolgerGraef/MSM/blob/main/app/models.py#L84)

 - check for any deleted samples or shares
NB: This had to be done after the flush, because if a parent sample / mountpoint was deleted,
the database would automatically set the corresponding foreign keys to NULL. Not sure if this
still applies since we are not really deleting samples anymore.

#### Signature

```python
def after_flush(session, flush_context):
    ...
```



## deleted_sample_handler

[Show source in models.py:14](https://github.com/HolgerGraef/MSM/blob/main/app/models.py#L14)

#### Signature

```python
def deleted_sample_handler(session, sample):
    ...
```



## deleted_share_handler

[Show source in models.py:58](https://github.com/HolgerGraef/MSM/blob/main/app/models.py#L58)

#### Signature

```python
def deleted_share_handler(session, share):
    ...
```



## load_user

[Show source in models.py:161](https://github.com/HolgerGraef/MSM/blob/main/app/models.py#L161)

#### Signature

```python
@login_manager.user_loader
def load_user(user_id):
    ...
```



## record_activity

[Show source in models.py:434](https://github.com/HolgerGraef/MSM/blob/main/app/models.py#L434)

#### Signature

```python
def record_activity(type, user=None, sample=None, description=None, commit=False):
    ...
```


