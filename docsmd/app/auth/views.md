# Views

[Mercury Sample Manager Index](../../README.md#mercury-sample-manager-index) /
[App](../index.md#app) /
[Auth](./index.md#auth) /
Views

> Auto-generated documentation for [app.auth.views](https://github.com/HolgerGraef/MSM/blob/master/app/auth/views.py) module.

## login

[Show source in views.py:10](https://github.com/HolgerGraef/MSM/blob/master/app/auth/views.py#L10)

#### Signature

```python
@auth.route("/login", methods=["GET", "POST"])
def login():
    ...
```



## logout

[Show source in views.py:112](https://github.com/HolgerGraef/MSM/blob/master/app/auth/views.py#L112)

#### Signature

```python
@auth.route("/logout")
@login_required
def logout():
    ...
```



## password_reset

[Show source in views.py:97](https://github.com/HolgerGraef/MSM/blob/master/app/auth/views.py#L97)

#### Signature

```python
@auth.route("/reset/<token>", methods=["GET", "POST"])
def password_reset(token):
    ...
```



## password_reset_request

[Show source in views.py:70](https://github.com/HolgerGraef/MSM/blob/master/app/auth/views.py#L70)

#### Signature

```python
@auth.route("/reset", methods=["GET", "POST"])
def password_reset_request():
    ...
```



