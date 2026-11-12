"""NEST-COUNT-R1: brute-force checks of the gadgets (the referee's own, by enumeration of every state)."""
import itertools, json
from pathlib import Path


def nae(*v):
    return len(set(v)) > 1


def proj(n_free, n_aux, test):
    """States of the free distinctions that extend to some state of the auxiliaries."""
    return {f for f in itertools.product((0, 1), repeat=n_free) if any(test(f, a) for a in itertools.product((0, 1), repeat=n_aux))}


out = {}
# P3a: x != y by four knots on x, y and three fresh distinctions
out["inequality"] = proj(2, 3, lambda f, a: nae(f[0], f[1], a[0]) and nae(f[0], f[1], a[1]) and nae(f[0], f[1], a[2]) and nae(*a)) == {(0, 1), (1, 0)}
# equality by two inequalities through m (each with its own three fresh distinctions)
neq = lambda x, y, a: nae(x, y, a[0]) and nae(x, y, a[1]) and nae(x, y, a[2]) and nae(*a)
out["equality"] = proj(2, 7, lambda f, a: neq(f[0], a[0], a[1:4]) and neq(a[0], f[1], a[4:7])) == {(0, 0), (1, 1)}
# the chain: NAE(x1..xm) iff some a1..a(m-3) with NAE(x1,x2,a1), NAE(~a1,x3,a2), ..., NAE(~a(m-3), x(m-1), xm)
chain = {}
for m in range(4, 9):
    def test(f, a, m=m):
        cur, ok = f[0], True
        for j in range(1, m - 2):
            ok &= nae(cur, f[j], a[j - 1])
            cur = 1 - a[j - 1]
        return ok and nae(cur, f[m - 2], f[m - 1])
    chain[m] = proj(m, m - 3, test) == {f for f in itertools.product((0, 1), repeat=m) if nae(*f)}
out["chain"] = chain
# the ten knots on five distinctions allow nothing
out["ten_knots_on_five"] = not any(all(nae(*(s[i] for i in t)) for t in itertools.combinations(range(5), 3))
                                   for s in itertools.product((0, 1), repeat=5))
print(json.dumps(out))
json.dump(out, open(Path(__file__).with_name("result_gadgets.json"), "w"), indent=1)
