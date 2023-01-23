# Actions

[Mercury Sample Manager Index](../../README.md#mercury-sample-manager-index) /
[App](../index.md#app) /
[Api](./index.md#api) /
Actions

> Auto-generated documentation for [app.api.actions](https://github.com/HolgerGraef/MSM/blob/master/app/api/actions.py) module.

## EmptySchema

[Show source in actions.py:17](https://github.com/HolgerGraef/MSM/blob/master/app/api/actions.py#L17)

#### Signature

```python
class EmptySchema(Schema):
    ...
```



## IdParameter

[Show source in actions.py:13](https://github.com/HolgerGraef/MSM/blob/master/app/api/actions.py#L13)

#### Signature

```python
class IdParameter(Schema):
    ...
```



## deleteaction

[Show source in actions.py:21](https://github.com/HolgerGraef/MSM/blob/master/app/api/actions.py#L21)

Delete an action from the database.
---
delete:
  parameters:
  - in: path
    schema: IdParameter
  responses:
    204:
      content:
        application/json:
          schema: EmptySchema
      description: Action deleted

#### Signature

```python
@api.route("/action/<int:id>", methods=["DELETE"])
@token_auth.login_required
def deleteaction(id):
    ...
```
