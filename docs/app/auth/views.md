# Views

[Msm Index](../../README.md#msm-index) /
[App](../index.md#app) /
[Auth](./index.md#auth) /
Views

> Auto-generated documentation for [app.auth.views](https://github.com/HolgerGraef/MSM/blob/main/app/auth/views.py) module.

- [Views](#views)
  - [login](#login)
  - [logout](#logout)
  - [password_reset](#password_reset)
  - [password_reset_request](#password_reset_request)

## login

[Show source in views.py:10](https://github.com/HolgerGraef/MSM/blob/main/app/auth/views.py#L10)

#### Signature

```python
@auth.route("/login", methods=["GET", "POST"])
def login():
    ...
```



## logout

[Show source in views.py:100](https://github.com/HolgerGraef/MSM/blob/main/app/auth/views.py#L100)

#### Signature

```python
@auth.route("/logout")
@login_required
def logout():
    ...
```



## password_reset

[Show source in views.py:85](https://github.com/HolgerGraef/MSM/blob/main/app/auth/views.py#L85)

#### Signature

```python
@auth.route("/reset/<token>", methods=["GET", "POST"])
def password_reset(token):
    ...
```



## password_reset_request

[Show source in views.py:61](https://github.com/HolgerGraef/MSM/blob/main/app/auth/views.py#L61)

#### Signature

```python
@auth.route("/reset", methods=["GET", "POST"])
def password_reset_request():
    ...
```


