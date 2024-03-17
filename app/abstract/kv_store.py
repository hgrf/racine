import redis

from flask import Flask

_kvs = {}
_redis = None


def kvs_set(key: str, value: object) -> None:
    if _redis is None:
        _kvs[key] = value
        return

    _redis.set(key, value)


def kvs_get(key):
    if _redis is None:
        return _kvs.get(key)

    return _redis.get(key)


def kvs_init_app(app: Flask) -> None:
    global _redis
    if app.config["REDIS"] is not None:
        _redis = redis.Redis(host=app.config["REDIS"]["host"], port=6379, decode_responses=True)
