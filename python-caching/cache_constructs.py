import functools
import cachetools


class Foobar:
    def __init__(self):
        self.cache = cachetools.LRUCache(maxsize=10)

    @property
    @cachetools.cachedmethod(lambda self: self.cache)
    def cached_method(self):
        # complex calculation or query here
        return ["some", "important", "result"]


import cachetools


class Foobar2:
    def __init__(self):
        self.cache1 = cachetools.LRUCache(maxsize=10)
        self.cache2 = cachetools.LRUCache(maxsize=10)

    @cachetools.cachedmethod(lambda self: self.cache1)
    def cached_method1(self, a, b, c):
        # complex calculation or query here
        return ["some", "important", "result", "1"]

    @cachetools.cachedmethod(lambda self: self.cache2)
    def cached_method2(self, a, b, c):
        # complex calculation or query here
        return ["some", "important", "result", "2"]


import cachetools
from cachetools.keys import hashkey
from functools import partial


class Foobar3:
    def __init__(self):
        self.cache = cachetools.LRUCache(maxsize=10)

    @cachetools.cachedmethod(
        lambda self: self.cache, key=partial(hashkey, "cached_method1")
    )
    def cached_method1(self, a, b, c):
        # complex calculation or query here
        return ["some", "important", "result", "1"]

    @cachetools.cachedmethod(
        lambda self: self.cache, key=partial(hashkey, "cached_method2")
    )
    def cached_method2(self, a, b, c):
        # complex calculation or query here
        return ["some", "important", "result", "2"]


import pickle
import cachetools

CACHING_DISABLED = False


def pickled_hashkey(*args, **kwargs):
    if CACHING_DISABLED:
        # every time we generate a cache miss
        return uuid.uuid4()

    pickled_args = pickle.dumps(args)
    pickled_kwargs = pickle.dumps(kwargs)
    return cachetools.keys.hashkey(pickled_args, pickled_kwargs)


if CACHING_DISABLED:
    cached_property = property
else:
    cached_property = functools.cached_property


@cachetools.cached(cache, key=pickled_hashkey)
def foobar(a, b, c):
    pass
