from timethese import cmpthese, pprint_cmp


class frozendict1(dict):
    def __hash__(self):
        return hash(frozenset(self.items()))


class frozendict2(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))


def hash_fd1():
    [hash(frozendict1({str(i): i + 1, str(i): i + 2})) for i in range(100)]


def hash_fd2():
    [hash(frozendict2({str(i): i + 1, str(i): i + 2})) for i in range(100)]


res = cmpthese(10000, [hash_fd1, hash_fd2], repeat=3,)

print(pprint_cmp(res))
