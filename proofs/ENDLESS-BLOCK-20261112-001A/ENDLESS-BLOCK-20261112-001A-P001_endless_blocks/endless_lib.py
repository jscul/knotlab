"""Endless blocks (research/ENDLESS-BLOCK-20261112-001/preregistration.md, ticket A).

Each distinction v of a pattern P becomes a copy of a harmony H (A70) on Z_P, P its period (the least common multiple of its states'
periods): distinctions (v, i), with H's kinds at every place. Each knot (x, y, z) of P becomes knots between the three copies built
from H's own knots {i, i + a, i + b}, (0, a, b) a kind of H:
- "every order": NAE((x, p), (y, q), (z, r)) for every ordering (p, q, r) of every knot of H (the pinning theorem's binding);
- "every order, lagged": the same with member v of knot e moved by a lag s_(e,v) along its copy;
- "one order": NAE((x, i), (y, i + a), (z, i + b)) for every kind and every i (a stitch of three harmonies by H's own kinds)."""
import itertools
import sys
from pathlib import Path

from pysat.solvers import Solver

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/BASES-WITHIN-20261112-001A/BASES-WITHIN-20261112-001A-P001_inner_series"))
import nest_lib as N  # noqa: E402


def harmonies():
    return N.harmonies()


def h_knots(h):
    P = h["P"]
    return sorted({tuple(sorted(((i) % P, (i + a) % P, (i + b) % P))) for (_, a, b) in h["kinds"] for i in range(P)})


def build(Ppat, h, mode, lags=None):
    """the substituted pattern: variables (v, i) -> v * P + i + 1"""
    n, Pk = Ppat
    P = h["P"]
    var = lambda v, i: v * P + (i % P) + 1
    cl = []
    for v in range(n):
        for (_, a, b) in h["kinds"]:
            for i in range(P):
                t = (var(v, i), var(v, i + a), var(v, i + b))
                cl += [list(t), [-x for x in t]]
    K = h_knots(h)
    for e, (x, y, z) in enumerate(Pk):
        if mode == "one order":
            for (_, a, b) in h["kinds"]:
                for i in range(P):
                    t = (var(x, i), var(y, i + a), var(z, i + b))
                    cl += [list(t), [-u for u in t]]
        else:
            sx, sy, sz = (lags or {}).get(e, (0, 0, 0))
            for k in K:
                for (p, q, r) in itertools.permutations(k):
                    t = (var(x, p + sx), var(y, q + sy), var(z, r + sz))
                    cl += [list(t), [-u for u in t]]
    return cl, n * P, var


def count(cl, nv, cap=100000):
    c = 0
    with Solver(name="cadical153", bootstrap_with=cl) as s:
        while s.solve():
            m = s.get_model()
            c += 1
            if c > cap:
                return None
            s.add_clause([-(i + 1) if m[i] > 0 else (i + 1) for i in range(nv)])
    return c


def tie_set(cl, nv, root):
    """the distinctions tied to root, with the relation (0 equal, 1 unequal); None if no state"""
    with Solver(name="cadical153", bootstrap_with=cl) as s:
        if not s.solve():
            return None
        m0 = s.get_model()
        val = lambda m, v: m[v - 1] > 0
        rel = {v: val(m0, root) ^ val(m0, v) for v in range(1, nv + 1)}
        cand = set(rel) - {root}
        tied = {root: 0}
        while cand:
            y = min(cand)
            if s.solve(assumptions=[root if val(m0, root) else -root, -y if val(m0, y) else y]):
                m = s.get_model()
                cand -= {v for v in cand if (val(m, root) ^ val(m, v)) != rel[v]}
            else:
                cand.discard(y)
                tied[y] = int(rel[y])
        return tied


def two_sharing_two():
    return (4, [(0, 1, 2), (0, 1, 3)])


def closed_chain(k):
    n = 2 * k
    return (n, [(2 * i, 2 * i + 1, (2 * i + 2) % n) for i in range(k)])


def ring(n):
    return (n, [(j, (j + 1) % n, (j + 2) % n) for j in range(n)])


def without(Ppat, e):
    n, Pk = Ppat
    return (n, [k for i, k in enumerate(Pk) if i != e])


def periods(h):
    return sorted({len(o) for o in h["orbits"]})


def open_chain(k):
    return (2 * k + 1, [(2 * i, 2 * i + 1, 2 * i + 2) for i in range(k)])


def min_periods(h):
    return sorted({len(o) for o in h["orbits"]})


def fixed_count(h, g):
    """states of H fixed by the shift by g (period dividing gcd(g, P))"""
    P = h["P"]
    return sum(1 for w in N.states(h) if all(w[i] == w[(i + g) % P] for i in range(P)))
