# Errors

[Msm Index](../../README.md#msm-index) /
[App](../index.md#app) /
[Main](./index.md#main) /
Errors

> Auto-generated documentation for [app.main.errors](https://github.com/HolgerGraef/MSM/blob/main/app/main/errors.py) module.

- [Errors](#errors)
  - [forbidden](#forbidden)
  - [internal_server_error](#internal_server_error)
  - [page_not_found](#page_not_found)
  - [unhandled_exception](#unhandled_exception)

## forbidden

[Show source in errors.py:7](https://github.com/HolgerGraef/MSM/blob/main/app/main/errors.py#L7)

#### Signature

```python
@main.app_errorhandler(403)
def forbidden(e):
    ...
```



## internal_server_error

[Show source in errors.py:17](https://github.com/HolgerGraef/MSM/blob/main/app/main/errors.py#L17)

#### Signature

```python
@main.app_errorhandler(500)
def internal_server_error(e):
    ...
```



## page_not_found

[Show source in errors.py:12](https://github.com/HolgerGraef/MSM/blob/main/app/main/errors.py#L12)

#### Signature

```python
@main.app_errorhandler(404)
def page_not_found(e):
    ...
```



## unhandled_exception

[Show source in errors.py:22](https://github.com/HolgerGraef/MSM/blob/main/app/main/errors.py#L22)

#### Signature

```python
@main.errorhandler(Exception)
def unhandled_exception(e):
    ...
```


