import functools
import weakref
import time

# use LRU cache in class/object context
# template:
# https://stackoverflow.com/questions/33672412/python-functools-lru-cache-with-class-methods-release-object


def omit_self(cache):
    def decorator(func):

        # wrapped_func function is called instead of func. usually it would be called
        # on every invocation instead of "func", but due to the setattr(self, ...)
        # futher down, wrapped_func is only called once! The setattr(self, ...)
        # replaces the object function with cached_self_less_func. Every subsequent
        # call to func is then directed towards cached_self_less_func
        # In summary:
        # 1. wrapped_func is called
        # 2. wrapped_func monkey-patches self to use cached_self_less_func
        # 3. cached_self_less_func is used from now on

        @functools.wraps(func)
        def wrapped_func(self, *args, **kwargs):

            # create a weak ref. If we would use a strong reference (aka self), the
            # instance never would die
            self_weak = weakref.ref(self)

            @functools.wraps(func)
            def self_less_func(*args, **kwargs):
                return func(self_weak(), *args, **kwargs)

            cached_self_less_func = cache(self_less_func)

            setattr(self, func.__name__, cached_self_less_func)
            return cached_self_less_func(*args, **kwargs)

        return wrapped_func

    return decorator


# test self-aware lru cache


class Foo:
    def __init__(self):
        self.ncalls = 0

    @omit_self(functools.lru_cache(maxsize=3))
    def blah(self, a, b):
        self.ncalls = self.ncalls + 1
        return a + b


f = Foo()

assert f.blah(1, 2) == 3
assert f.ncalls == 1
assert f.blah(1, 2) == 3
assert f.ncalls == 1
assert f.blah(2, 2) == 4
assert f.ncalls == 2
assert f.blah(3, 2) == 5
assert f.ncalls == 3
assert f.blah(4, 2) == 6
assert f.ncalls == 4
assert f.blah(1, 2) == 3
assert f.ncalls == 5


# remodel LRU cache to TTL LRU cache
# template:
# https://stackoverflow.com/questions/31771286/python-in-memory-cache-with-time-to-live


def add_ttl(cache, ttl=3600):
    def decorator(func):
        # add ttl
        start_time = time.time()

        def ttl_func(ttl_hash, *args, **kwargs):
            return func(*args, **kwargs)

        cached_ttl_func = cache(ttl_func)

        @functools.wraps(func)
        def wrapped_func(*args, **kwargs):
            ttl_hash = int(time.time() - start_time) // ttl
            return cached_ttl_func(ttl_hash, *args, **kwargs)

        return wrapped_func

    return decorator


# test add_ttl

ttl_ncalls = 0


@add_ttl(functools.lru_cache(maxsize=3), ttl=1)
def ttl_blah(a, b):
    global ttl_ncalls
    ttl_ncalls = ttl_ncalls + 1
    return a + b


# test self-aware lru cache

assert ttl_blah(1, 2) == 3
assert ttl_ncalls == 1
assert ttl_blah(1, 2) == 3
assert ttl_ncalls == 1
assert ttl_blah(2, 2) == 4
assert ttl_ncalls == 2
assert ttl_blah(3, 2) == 5
assert ttl_ncalls == 3
assert ttl_blah(4, 2) == 6
assert ttl_ncalls == 4
assert ttl_blah(1, 2) == 3
assert ttl_ncalls == 5

# test ttl functionality
assert ttl_blah(1, 2) == 3
assert ttl_ncalls == 5
time.sleep(1)
assert ttl_blah(1, 2) == 3
assert ttl_ncalls == 6
