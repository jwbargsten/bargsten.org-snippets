import functools
import pickle
import time
import json
from timethese import pprint_cmp, cmpthese


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


@pickled_lru_cache(functools.lru_cache(maxsize=100))
def pickled_lru(a, b):
    return a + b[0]


@functools.lru_cache(maxsize=100)
def py_lru(a, b):
    return a + b[0]


def run_pickled_lru():
    [pickled_lru(i, (i,)) for i in range(100)]


def run_py_lru():
    [py_lru(i, (i,)) for i in range(100)]


res = cmpthese(10000, [run_py_lru, run_pickled_lru], repeat=3)
print(pprint_cmp(res))
