# Models

[Mercury Sample Manager Index](../README.md#mercury-sample-manager-index) /
[App](./index.md#app) /
Models

> Auto-generated documentation for [app.models](https://github.com/HolgerGraef/MSM/blob/master/app/models.py) module.

## Action

[Show source in models.py:300](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L300)

#### Signature

```python
class Action(db.Model):
    ...
```

### Action().has_read_access

[Show source in models.py:318](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L318)

#### Signature

```python
def has_read_access(self, user):
    ...
```

### Action().has_write_access

[Show source in models.py:327](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L327)

#### Signature

```python
def has_write_access(self, user):
    ...
```



## Activity

[Show source in models.py:443](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L443)

#### Signature

```python
class Activity(db.Model):
    ...
```



## ActivityType

[Show source in models.py:461](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L461)

#### Signature

```python
class ActivityType(db.Model):
    ...
```



## LinkUserNews

[Show source in models.py:394](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L394)

#### Signature

```python
class LinkUserNews(db.Model):
    ...
```



## News

[Show source in models.py:331](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L331)

#### Attributes

- `recipient_id` - recipient can be either all users, a specific user, or all users who share a given sample: `db.Column(db.Integer, db.ForeignKey('users.id'))`

- `recipients` - action = db.relationship('Action', backref="news"): `db.relationship('LinkUserNews', backref='news', foreign_keys='LinkUserNews.news_id', cascade='delete')`


#### Signature

```python
class News(db.Model):
    ...
```

### News().dispatch

[Show source in models.py:352](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L352)

#### Signature

```python
def dispatch(self):
    ...
```

### News().render_content

[Show source in models.py:381](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L381)

#### Signature

```python
def render_content(self):
    ...
```



## SMBResource

[Show source in models.py:404](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L404)

#### Signature

```python
class SMBResource(db.Model):
    ...
```



## Sample

[Show source in models.py:186](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L186)

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

[Show source in models.py:237](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L237)

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

[Show source in models.py:282](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L282)

#### Signature

```python
@property
def logical_parent(self):
    ...
```

### Sample().mountedsamples

[Show source in models.py:268](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L268)

make a list of samples that are mounted in this one by the current user

#### Signature

```python
@property
def mountedsamples(self):
    ...
```



## Share

[Show source in models.py:419](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L419)

#### Signature

```python
class Share(db.Model):
    ...
```



## Upload

[Show source in models.py:430](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L430)

#### Signature

```python
class Upload(db.Model):
    ...
```



## User

[Show source in models.py:115](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L115)

#### Signature

```python
class User(UserMixin, db.Model):
    ...
```

### User().directshares

[Show source in models.py:167](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L167)

determine the user's direct shares that are not mounted anywhere in his tree
(i.e. they are at the top level)

#### Signature

```python
@property
def directshares(self):
    ...
```

### User().generate_reset_token

[Show source in models.py:149](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L149)

#### Signature

```python
def generate_reset_token(self, expiration=3600):
    ...
```

### User().password

[Show source in models.py:138](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L138)

#### Signature

```python
@property
def password(self):
    ...
```

### User().password

[Show source in models.py:142](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L142)

#### Signature

```python
@password.setter
def password(self, password):
    ...
```

### User.reset_password

[Show source in models.py:153](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L153)

#### Signature

```python
@staticmethod
def reset_password(token, new_password):
    ...
```

### User().verify_password

[Show source in models.py:146](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L146)

#### Signature

```python
def verify_password(self, password):
    ...
```



## after_flush

[Show source in models.py:97](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L97)

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

[Show source in models.py:14](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L14)

#### Signature

```python
def deleted_sample_handler(session, sample):
    ...
```



## deleted_share_handler

[Show source in models.py:66](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L66)

#### Signature

```python
def deleted_share_handler(session, share):
    ...
```



## load_user

[Show source in models.py:181](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L181)

#### Signature

```python
@login_manager.user_loader
def load_user(user_id):
    ...
```



## record_activity

[Show source in models.py:472](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L472)

#### Signature

```python
def record_activity(type, user=None, sample=None, description=None, commit=False):
    ...
```
