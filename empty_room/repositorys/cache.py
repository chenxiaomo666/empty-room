# -*- coding:utf-8 -*-

from flask import current_app as app
import functools
import pickle
import hashlib
import redis

cache_redis_client = redis.StrictRedis.from_url(app.config.get("REDIS_URL"))


def cache(key_prefix: str = "", timeout: int = 10):
    """
    A decorator of redis base function cache
    """
    def decorator(func):
        @functools.wraps(func)
        def warpper(*args, **kwargs):
            _prefix = "cache:{}".format(key_prefix if key_prefix else func.__name__)
            cache_key = _prepare_key(_prefix, *args, **kwargs)
            cached = cache_redis_client.get(cache_key)
            if cached:
                return pickle.loads(cached)
            result = func(*args, **kwargs)
            cache_redis_client.set(cache_key, pickle.dumps(result), ex=timeout)
            return result
        return warpper
    return decorator


def _prepare_key(key, *args, **kwargs):

    if not args and not kwargs:
        return key

    items = sorted(kwargs.items())
    hashable_args = (args, tuple(items))
    args_key = hashlib.md5(pickle.dumps(hashable_args)).hexdigest()

    return "{}:{}".format(key, args_key)
