# Shares

[Mercury Sample Manager Index](../../README.md#mercury-sample-manager-index) /
[App](../index.md#app) /
[Api](./index.md#api) /
Shares

> Auto-generated documentation for [app.api.shares](https://github.com/HolgerGraef/MSM/blob/master/app/api/shares.py) module.

## deleteshare

[Show source in shares.py:10](https://github.com/HolgerGraef/MSM/blob/master/app/api/shares.py#L10)

#### Signature

```python
@api.route("/share/<int:id>", methods=["DELETE"])
@token_auth.login_required
def deleteshare(id):
    ...
```
