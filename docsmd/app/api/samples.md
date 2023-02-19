# Samples

[Mercury Sample Manager Index](../../README.md#mercury-sample-manager-index) /
[App](../index.md#app) /
[Api](./index.md#api) /
Samples

> Auto-generated documentation for [app.api.samples](https://github.com/HolgerGraef/MSM/blob/master/app/api/samples.py) module.

## deletesample

[Show source in samples.py:10](https://github.com/HolgerGraef/MSM/blob/master/app/api/samples.py#L10)

Delete a sample from the database.
---
delete:
  operationId: deleteSample
  parameters:
  - in: path
    schema: IdParameter
  responses:
    204:
      content:
        application/json:
          schema: EmptySchema
      description: Sample deleted

#### Signature

```python
@api.route("/sample/<int:id>", methods=["DELETE"])
@token_auth.login_required
def deletesample(id):
    ...
```
