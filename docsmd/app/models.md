# Models

[Mercury Sample Manager Index](../README.md#mercury-sample-manager-index) /
[App](./index.md#app) /
Models

> Auto-generated documentation for [app.models](https://github.com/HolgerGraef/MSM/blob/master/app/models.py) module.

## Action

[Show source in models.py:325](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L325)

#### Signature

```python
class Action(db.Model):
    ...
```

### Action().has_read_access

[Show source in models.py:343](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L343)

#### Signature

```python
def has_read_access(self, user):
    ...
```

### Action().has_write_access

[Show source in models.py:352](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L352)

#### Signature

```python
def has_write_access(self, user):
    ...
```



## Activity

[Show source in models.py:468](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L468)

#### Signature

```python
class Activity(db.Model):
    ...
```



## ActivityType

[Show source in models.py:486](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L486)

#### Signature

```python
class ActivityType(db.Model):
    ...
```



## LinkUserNews

[Show source in models.py:419](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L419)

#### Signature

```python
class LinkUserNews(db.Model):
    ...
```



## News

[Show source in models.py:356](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L356)

#### Attributes

- `recipient_id` - recipient can be either all users, a specific user, or all users who share a given sample: `db.Column(db.Integer, db.ForeignKey('users.id'))`

- `recipients` - action = db.relationship('Action', backref="news"): `db.relationship('LinkUserNews', backref='news', foreign_keys='LinkUserNews.news_id', cascade='delete')`


#### Signature

```python
class News(db.Model):
    ...
```

### News().dispatch

[Show source in models.py:377](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L377)

#### Signature

```python
def dispatch(self):
    ...
```

### News().render_content

[Show source in models.py:406](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L406)

#### Signature

```python
def render_content(self):
    ...
```



## SMBResource

[Show source in models.py:429](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L429)

#### Signature

```python
class SMBResource(db.Model):
    ...
```



## Sample

[Show source in models.py:211](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L211)

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

[Show source in models.py:262](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L262)

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

[Show source in models.py:307](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L307)

#### Signature

```python
@property
def logical_parent(self):
    ...
```

### Sample().mountedsamples

[Show source in models.py:293](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L293)

make a list of samples that are mounted in this one by the current user

#### Signature

```python
@property
def mountedsamples(self):
    ...
```



## Share

[Show source in models.py:444](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L444)

#### Signature

```python
class Share(db.Model):
    ...
```



## Upload

[Show source in models.py:455](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L455)

#### Signature

```python
class Upload(db.Model):
    ...
```



## User

[Show source in models.py:119](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L119)

#### Signature

```python
class User(UserMixin, db.Model):
    ...
```

### User.check_token

[Show source in models.py:198](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L198)

#### Signature

```python
@staticmethod
def check_token(token):
    ...
```

### User().directshares

[Show source in models.py:173](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L173)

determine the user's direct shares that are not mounted anywhere in his tree
(i.e. they are at the top level)

#### Signature

```python
@property
def directshares(self):
    ...
```

### User().generate_reset_token

[Show source in models.py:155](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L155)

#### Signature

```python
def generate_reset_token(self, expiration=3600):
    ...
```

### User().get_token

[Show source in models.py:186](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L186)

#### Signature

```python
def get_token(self, expires_in=3600):
    ...
```

### User().password

[Show source in models.py:144](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L144)

#### Signature

```python
@property
def password(self):
    ...
```

### User().password

[Show source in models.py:148](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L148)

#### Signature

```python
@password.setter
def password(self, password):
    ...
```

### User.reset_password

[Show source in models.py:159](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L159)

#### Signature

```python
@staticmethod
def reset_password(token, new_password):
    ...
```

### User().revoke_token

[Show source in models.py:195](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L195)

#### Signature

```python
def revoke_token(self):
    ...
```

### User().verify_password

[Show source in models.py:152](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L152)

#### Signature

```python
def verify_password(self, password):
    ...
```



## after_flush

[Show source in models.py:101](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L101)

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

[Show source in models.py:18](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L18)

#### Signature

```python
def deleted_sample_handler(session, sample):
    ...
```



## deleted_share_handler

[Show source in models.py:70](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L70)

#### Signature

```python
def deleted_share_handler(session, share):
    ...
```



## load_user

[Show source in models.py:206](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L206)

#### Signature

```python
@login_manager.user_loader
def load_user(user_id):
    ...
```



## record_activity

[Show source in models.py:497](https://github.com/HolgerGraef/MSM/blob/master/app/models.py#L497)

#### Signature

```python
def record_activity(type, user=None, sample=None, description=None, commit=False):
    ...
```
