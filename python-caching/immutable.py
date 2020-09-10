class frozendict(dict):
    def __hash__(self):
        return hash(frozenset(self.items()))

def to_immutable(v):
    if isinstance(v, dict):
        return frozendict(v)
    if isinstance(v, list):
        return tuple(v)
    if isinstance(v, set):
        return frozenset(v)
    raise TypeError(f"cannot convert {type(v)} to immutable counterpart")


class Foo:
    pass
assert to_immutable({2:3}) == frozendict({2:3})
assert to_immutable([2,3]) == (2,3)
assert to_immutable([2,3]) != [2,3]
assert to_immutable({2,3}) == frozenset([2,3])
assert to_immutable(Foo())
