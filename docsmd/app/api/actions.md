# Actions

[Mercury Sample Manager Index](../../README.md#mercury-sample-manager-index) /
[App](../index.md#app) /
[Api](./index.md#api) /
Actions

> Auto-generated documentation for [app.api.actions](https://github.com/HolgerGraef/MSM/blob/master/app/api/actions.py) module.

## CreateActionError

[Show source in actions.py:25](https://github.com/HolgerGraef/MSM/blob/master/app/api/actions.py#L25)

#### Signature

```python
class CreateActionError(Schema):
    ...
```



## NewActionFormContent

[Show source in actions.py:19](https://github.com/HolgerGraef/MSM/blob/master/app/api/actions.py#L19)

#### Signature

```python
class NewActionFormContent(Schema):
    ...
```



## SampleParameter

[Show source in actions.py:15](https://github.com/HolgerGraef/MSM/blob/master/app/api/actions.py#L15)

#### Signature

```python
class SampleParameter(Schema):
    ...
```



## createaction

[Show source in actions.py:29](https://github.com/HolgerGraef/MSM/blob/master/app/api/actions.py#L29)

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

[Show source in actions.py:88](https://github.com/HolgerGraef/MSM/blob/master/app/api/actions.py#L88)

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
