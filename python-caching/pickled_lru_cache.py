import time
import json
from timethese import pprint_cmp, cmpthese
from collections import namedtuple
import json
import six
import cachetools
import cachetools.keys

import functools
import pickle

def pickled_lru_cache(cache):
    def pickled_lru_cache_decorator(func):
        def func_with_pickled_args(pickled_args, pickled_kwargs):
            args = pickle.loads(pickled_args)
            kwargs = pickle.loads(pickled_kwargs)
            return func(*args, **kwargs)

        cached_func = cache(func_with_pickled_args)

        @functools.wraps(func)
        def pickled_cached_func(*args, **kwargs):
            pickled_args = pickle.dumps(args)
            pickled_kwargs = pickle.dumps(kwargs)
            return cached_func(pickled_args, pickled_kwargs)

        pickled_cached_func.cache_info = cached_func.cache_info
        pickled_cached_func.cache_clear = cached_func.cache_clear

        return pickled_cached_func

    return pickled_lru_cache_decorator


# taken from https://gist.github.com/adah1972/f4ec69522281aaeacdba65dbee53fade
# for performance comparison
Serialized = namedtuple("Serialized", "json")


def hashable_cache(cache):
    def hashable_cache_internal(func):
        def deserialize(value):
            if isinstance(value, Serialized):
                return json.loads(value.json)
            else:
                return value

        def func_with_serialized_params(*args, **kwargs):
            _args = tuple([deserialize(arg) for arg in args])
            _kwargs = {k: deserialize(v) for k, v in six.viewitems(kwargs)}
            return func(*_args, **_kwargs)

        cached_func = cache(func_with_serialized_params)

        @functools.wraps(func)
        def hashable_cached_func(*args, **kwargs):
            _args = tuple(
                [
                    Serialized(json.dumps(arg, sort_keys=True))
                    if type(arg) in (list, dict)
                    else arg
                    for arg in args
                ]
            )
            _kwargs = {
                k: Serialized(json.dumps(v, sort_keys=True))
                if type(v) in (list, dict)
                else v
                for k, v in kwargs.items()
            }
            return cached_func(*_args, **_kwargs)

        hashable_cached_func.cache_info = cached_func.cache_info
        hashable_cached_func.cache_clear = cached_func.cache_clear
        return hashable_cached_func

    return hashable_cache_internal



ncalls = 0


@pickled_lru_cache(functools.lru_cache(maxsize=3))
def function_that_takes_long(*args, **kwargs):
    global ncalls
    ncalls = ncalls + 1
    return json.dumps({"args": args, "kwargs": kwargs})


result = function_that_takes_long(2, 3, [2, 3], {2: 3}, a=2, b=3, c=[2, 3], d={2: 3})

expected = json.dumps(
    {
        "args": [2, 3, [2, 3], {2: 3}],
        "kwargs": {"a": 2, "b": 3, "c": [2, 3], "d": {2: 3}},
    }
)

assert result == expected
assert ncalls == 1

result2 = function_that_takes_long(2, 3, [2, 3], {2: 3}, a=2, b=3, c=[2, 3], d={2: 3})
assert result2 == expected
assert ncalls == 1

result3 = function_that_takes_long(1, 3, [2, 3], {2: 3}, a=2, b=3, c=[2, 3], d={2: 3})
assert result3 != expected
assert ncalls == 2

def pickled_hashkey(*args, **kwargs):
    pickled_args = pickle.dumps(args)
    pickled_kwargs = pickle.dumps(kwargs)
    return cachetools.keys.hashkey(pickled_args, pickled_kwargs)

@pickled_lru_cache(functools.lru_cache(maxsize=100))
def pickled_lru(u, v, *args, **kwargs):
    return u + v[0]


@functools.lru_cache(maxsize=100)
def py_lru(u, v, *args, **kwargs):
    return u + v[0]


@hashable_cache(functools.lru_cache(maxsize=100))
def hashable_lru(u, v, *args, **kwargs):
    return u + v[0]

@cachetools.cached(cachetools.LRUCache(maxsize=100), key=pickled_hashkey)
def cachetools_lru(u, v, *args, **kwargs):
    return u + v[0]

def run_pickled_lru():
    [pickled_lru(i, (i, i, i, i)) for i in range(100)]


def run_py_lru():
    [py_lru(i, (i, i, i, i)) for i in range(100)]


def run_hashable_lru():
    [hashable_lru(i, (i, i, i, i)) for i in range(100)]

def run_cachetools_lru():
    [cachetools_lru(i, (i, i, i, i)) for i in range(100)]




res = cmpthese(10000, [run_py_lru, run_pickled_lru, run_hashable_lru, run_cachetools_lru], repeat=3)
print(pprint_cmp(res))


def run_pickled_lru2():
    [
        pickled_lru(
            i,
            (i + 1,),
            [i, i + 1],
            {i: i + 1},
            a=i,
            b=i + 1,
            c=[i, i + 1],
            d={i: i + 1},
        )
        for i in range(100)
    ]


def run_hashable_lru2():
    [
        hashable_lru(
            i,
            (i + 1,),
            [i, i + 1],
            {i: i + 1},
            a=i,
            b=i + 1,
            c=[i, i + 1],
            d={i: i + 1},
        )
        for i in range(100)
    ]

def run_cachetools_lru2():
    [
        cachetools_lru(
            i,
            (i + 1,),
            [i, i + 1],
            {i: i + 1},
            a=i,
            b=i + 1,
            c=[i, i + 1],
            d={i: i + 1},
        )
        for i in range(100)
    ]

res2 = cmpthese(10000, [run_pickled_lru2, run_hashable_lru2, run_cachetools_lru2], repeat=3)
print(pprint_cmp(res2))
