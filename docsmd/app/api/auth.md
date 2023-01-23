# Auth

[Mercury Sample Manager Index](../../README.md#mercury-sample-manager-index) /
[App](../index.md#app) /
[Api](./index.md#api) /
Auth

> Auto-generated documentation for [app.api.auth](https://github.com/HolgerGraef/MSM/blob/master/app/api/auth.py) module.

## basic_auth_error

[Show source in auth.py:16](https://github.com/HolgerGraef/MSM/blob/master/app/api/auth.py#L16)

#### Signature

```python
@basic_auth.error_handler
def basic_auth_error(status):
    ...
```



## token_auth_error

[Show source in auth.py:26](https://github.com/HolgerGraef/MSM/blob/master/app/api/auth.py#L26)

#### Signature

```python
@token_auth.error_handler
def token_auth_error(status):
    ...
```



## verify_password

[Show source in auth.py:9](https://github.com/HolgerGraef/MSM/blob/master/app/api/auth.py#L9)

#### Signature

```python
@basic_auth.verify_password
def verify_password(username, password):
    ...
```



## verify_token

[Show source in auth.py:21](https://github.com/HolgerGraef/MSM/blob/master/app/api/auth.py#L21)

#### Signature

```python
@token_auth.verify_token
def verify_token(token):
    ...
```
