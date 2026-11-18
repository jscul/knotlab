"""MEET-TWIST-20261118-001B frozen check, for the shared runner (docs/tooling/shared-runner.md).

melib.py is MEET-ORDERS-20261118-001B's engine, copied unchanged (same sha256).

Case T|n0|d|i: bracketing i of the line of n0 (mark g = {m, 0}) against the same knots with the mark moved one step to {0, 1}
(renamed i -> i - 1 mod n0, so its line is again 0..m). Labelled KF3 from both to n0 + d. At every reached state of the first
below depth: the odd sets (or "a state was added"), KF3's options, each mapped knot by knot by Lemma 2's table and renamed, against
the options at the image state of the second; and at every level the joint labelled law of (states, pairs) mapped by the twist
(each distinction keeps its odd set, the mark moves) against the second's.
"""
import sys
from collections import defaultdict, Counter
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import melib as M

CASES = [(5, 4), (6, 4), (7, 4), (8, 3), (9, 3)]


def cases():
    for n0, d in CASES:
        for i, T in enumerate(M.bracketings(0, n0 - 1)):
            yield f"T|{n0}|{d}|{i}", {"n0": n0, "depth": d, "knots": T}


def moved(T, n0):
    rho = lambda v: (v - 1) % n0
    return [tuple(sorted(rho(v) for v in k)) for k in T], rho


def ren(rho, n0):
    return lambda v: rho(v) if v < n0 else v


def state_image(S, n, n0, rho, sets):
    """The twist: the mark moves from {m, 0} to {0, 1}; every distinction keeps its odd set; then rename by rho."""
    m = n0 - 1
    f = ren(rho, n0)
    out = []
    for s in S:
        x = [(s >> v) & 1 for v in range(n0)]
        y = list(x)
        y[0] = x[m] ^ x[0] ^ x[1]
        z = [0] * n
        for v in range(n0):
            z[f(v)] = y[v]
        for i, O in enumerate(sets):
            z[n0 + i] = sum(y[v] for v in O) & 1
        out.append(sum(b << v for v, b in enumerate(z)))
    return tuple(sorted(out))


def G_image(G, rho, n0):
    f = ren(rho, n0)
    return frozenset((min(f(a), f(b)), max(f(a), f(b))) for a, b in G)


def normal(knot, r):
    """('b', {u, v}) for B(u, r, v); ('g', (u, x)) for a knot pinning r = x where u and x differ (B(u, x, r))."""
    x, y, z = knot
    if y == r:
        return ("b", frozenset((x, z)))
    if z == r:
        return ("g", (x, y))
    return ("g", (z, y))


def lemma2(nk, Or, O, w=0):
    """Image of a normalised knot under moving the mark past w (Lemma 2's table)."""
    def has(X):
        return w in X
    if nk[0] == "b":
        u, v = sorted(nk[1])
        if not has(O[u] ^ O[v]):
            return nk
        x = u if not has(Or ^ O[u]) else v
        other = v if x == u else u
        return ("g", (other, x))
    u, x = nk[1]
    if has(O[u] ^ O[x]):
        return ("b", frozenset((u, x)))
    if not has(Or ^ O[x]):
        return nk
    return ("g", (x, u))


def rename_normal(nk, f):
    if nk[0] == "b":
        return ("b", frozenset(f(v) for v in nk[1]))
    return ("g", (f(nk[1][0]), f(nk[1][1])))


def options(S, n, G, n0):
    cost, top = M.zero_cost_top(S, n, G)
    out = []
    for a0, a1, ks in top:
        S2 = M.apply(S, n, a0, a1)
        sets = M.odd_sets(S2, n + 1, n0)
        out.append((frozenset(normal(k, n) for k in ks), sets[-1] if sets else None))
    return cost, out


def run(case_id, p):
    n0, d, T = p["n0"], p["depth"], [tuple(k) for k in p["knots"]]
    T2, rho = moved(T, n0)
    f = ren(rho, n0)
    A = M.exact(n0, T, n0 + d, use_canon=False)
    B = M.exact(n0, T2, n0 + d, use_canon=False)
    rows = []
    for lev in range(d + 1):
        LA, LB = A[lev]["dist"], B[lev]["dist"]
        n = n0 + lev
        img = defaultdict(Fraction)
        added = 0
        opt_ok = opt_bad = 0
        for (S, G), q in LA.items():
            sets = M.odd_sets(S, n, n0)
            if sets is None:
                added += 1
                continue
            S2, G2 = state_image(S, n, n0, rho, sets), G_image(G, rho, n0)
            img[(S2, G2)] += q
            if lev < d:
                O = {v: frozenset([v]) for v in range(n0)}
                for i, X in enumerate(sets):
                    O[n0 + i] = frozenset(X)
                ca, oa = options(S, n, G, n0)
                cb, ob = options(S2, n, G2, n0)
                mapped = Counter()
                for knots, Or in oa:
                    if Or is None:
                        mapped["state added"] += 1
                        continue
                    Or = frozenset(Or)
                    mapped[frozenset(rename_normal(lemma2(k, Or, O), f) for k in knots)] += 1
                target = Counter(knots for knots, _ in ob)
                if ca == cb == 0 and mapped == target:
                    opt_ok += 1
                else:
                    opt_bad += 1
        rows.append({"n": n, "labelled": len(LA), "states_added": added, "law_carried": added == 0 and dict(img) == LB,
                     "option_states_ok": opt_ok, "option_states_bad": opt_bad})
    return {"n0": n0, "depth": d, "knots": T, "moved": T2, "ordered": M.nesting(T, 0, n0 - 1, ordered=True), "levels": rows}


if __name__ == "__main__":
    print(sum(1 for _ in cases()), "cases")
