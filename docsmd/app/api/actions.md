# Actions

[Mercury Sample Manager Index](../../README.md#mercury-sample-manager-index) /
[App](../index.md#app) /
[Api](./index.md#api) /
Actions

> Auto-generated documentation for [app.api.actions](https://github.com/HolgerGraef/MSM/blob/master/app/api/actions.py) module.

## CreateActionError

[Show source in actions.py:24](https://github.com/HolgerGraef/MSM/blob/master/app/api/actions.py#L24)

#### Signature

```python
class CreateActionError(Schema):
    ...
```



## EmptySchema

[Show source in actions.py:32](https://github.com/HolgerGraef/MSM/blob/master/app/api/actions.py#L32)

#### Signature

```python
class EmptySchema(Schema):
    ...
```



## IdParameter

[Show source in actions.py:28](https://github.com/HolgerGraef/MSM/blob/master/app/api/actions.py#L28)

#### Signature

```python
class IdParameter(Schema):
    ...
```



## NewActionFormContent

[Show source in actions.py:18](https://github.com/HolgerGraef/MSM/blob/master/app/api/actions.py#L18)

#### Signature

```python
class NewActionFormContent(Schema):
    ...
```



## SampleParameter

[Show source in actions.py:14](https://github.com/HolgerGraef/MSM/blob/master/app/api/actions.py#L14)

#### Signature

```python
class SampleParameter(Schema):
    ...
```



## createaction

[Show source in actions.py:36](https://github.com/HolgerGraef/MSM/blob/master/app/api/actions.py#L36)

Create an action in the database.
---
put:
  operationId: createAction
  parameters:
  - in: path
    schema: SampleParameter
  requestBody:
    required: true
    content:
      application/x-www-form-urlencoded:
        schema: NewActionFormContent
  responses:
    201:
      content:
        application/json:
          schema: EmptySchema
      description: Action created
    400:
      content:
        application/json:
          schema: CreateActionError
      description: Failed to create action

#### Signature

```python
@api.route("/action/<int:sampleid>", methods=["PUT"])
@token_auth.login_required
def createaction(sampleid):
    ...
```



## deleteaction

[Show source in actions.py:95](https://github.com/HolgerGraef/MSM/blob/master/app/api/actions.py#L95)

Delete an action from the database.
---
delete:
  operationId: deleteAction
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
