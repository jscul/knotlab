"""MID-RULE-20261118-001B-E001: a rule whose second phase reads only the move's knots.

MID2: while the knots carry no filled knot (no two splits cross), any fill; afterwards only fills whose new distinction is the middle
of two or more of their knots; else a one-split subdivision.  ONE: the same with "at most one end knot" in place of "two or more
middle knots" (MID2's sets have at most one end knot).  ANY: the same with any fill (the positive control).  Two forms:
- knot-local (MID2K): KF3's moves (knots only on pairs that already share one), uniform over knot sets, every knot recorded
  (KNOT-SWITCH-20261118-001B's knotlib.py, pinned);
- free (MID2F): knots on any old pairs, uniform over distinct extensions; a fill qualifies when some certificate of at most three
  consistent knots, two or more of them middle knots, forces it.
"""
import itertools
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.append(os.path.join(ROOT, "experiments", "KNOT-SWITCH-20261118-001B", "KNOT-SWITCH-20261118-001B-E001_switch"))
import knotlib as K  # noqa: E402

M, L, P = K.M, K.L, K.P


def middles(ks, n):
    return sum(1 for k in ks if k[1] == n)


def ends(ks, n):
    return sum(1 for k in ks if k[1] != n)


def knot_test(rule, ks, n):
    return {"MID2": middles(ks, n) >= 2, "ONE": ends(ks, n) <= 1, "ANY": True}[rule]


def mid2k_options(S, n, G, crossed, rule="MID2"):
    mv = L.moves(S, n, G)
    N = len(S)
    zero = [x for x in mv if P.pc(x[0]) + P.pc(x[1]) == N]
    good = zero if not crossed else [x for x in zero if knot_test(rule, x[2], n)]
    if good:
        return good, "fill"
    return [x for x in mv if L.is_sub(x[2], n, S)], "sub"


def certified(S, n, F0, F1, rule):
    """Whether the fill (0 on F0, 1 on F1) is forced by at most three consistent knots on old pairs that pass the rule's test: two
    or more middle knots B(u, r, v) (MID2), or at most one end knot (ONE)."""
    O, Z, full = M.cols(S, n)
    mids, ends = [], []
    for u, v in itertools.combinations(range(n), 2):
        eq = (O[u] & O[v]) | (Z[u] & Z[v])
        ne = full ^ eq
        p0, p1 = Z[u] & Z[v], O[u] & O[v]                 # middle knot: r = u where u = v
        if not (p0 & F1) and not (p1 & F0):
            mids.append(p0 | p1)
        for p0, p1 in ((ne & Z[v], ne & O[v]), (ne & Z[u], ne & O[u])):       # end knots
            if not (p0 & F1) and not (p1 & F0):
                ends.append(p0 | p1)
    mids = sorted(set(mids), key=P.pc, reverse=True)
    ends = sorted(set(ends), key=P.pc, reverse=True)
    if rule == "ONE":
        for a in mids:                                       # one middle knot, alone or with one end knot
            if a == full:
                return True
            need = full ^ a
            if any((e & need) == need for e in ends):
                return True
    for a, b in itertools.combinations(mids, 2):
        c = a | b
        if c == full:
            return True
        need = full ^ c
        if any((m & need) == need for m in mids) or any((e & need) == need for e in ends):
            return True
    return False


def mid2f_options(S, n, rule="MID2"):
    sp, Gc = P.crossing_graph(S, n)
    F = P.fills(S, n)
    if Gc.number_of_edges() == 0 or rule == "ANY":
        good = F
    else:
        good = [f for f in F if certified(S, n, f[0], f[1], rule)]
    if good:
        return good, "fill"
    return sorted(L.free_subs(S, n)), "sub"


def reading(S, n):
    k, lam = P.kl(S, n)
    g = P.grid(S, n)
    return {"n": n, "N": len(S), "k": k, "lam": lam, "full_grid": g is not None and len(g[1]) == 2,
            "grid": g[1] if g else None, "nothing_crosses": K.nothing_crosses(S, n)}


def grow_k(knots0, n0, nmax, seed_value, rule="MID2"):
    rng = random.Random(seed_value)
    S, G, knots, n = M.base(n0, knots0), M.pairs_of(knots0), list(knots0), n0
    tr = [{**reading(S, n), "kind": "start"}]
    while n < nmax:
        if len(S) > 120:
            tr.append({"n": n + 1, "stopped": "state limit"})
            break
        ops, kind = mid2k_options(S, n, G, not tr[-1]["nothing_crosses"], rule)
        if not ops:
            tr.append({"n": n + 1, "stopped": "no option"})
            break
        a0, a1, ks = rng.choice(ops)
        S2 = M.apply(S, n, a0, a1)
        cost = len(S2) - len(S)
        S, G, knots, n = S2, G | M.pairs_of(ks), knots + list(ks), n + 1
        tr.append({**reading(S, n), "kind": "fill" if cost == 0 else "sub", "options": len(ops), "middles": middles(ks, n - 1)})
    return tr


def grow_f(S, n, nmax, seed_value, rule="MID2"):
    rng = random.Random(seed_value)
    S = tuple(sorted(S))
    tr = [{**reading(S, n), "kind": "start"}]
    while n < nmax:
        if len(S) > 60:
            tr.append({"n": n + 1, "stopped": "state limit"})
            break
        ops, kind = mid2f_options(S, n, rule)
        if not ops:
            tr.append({"n": n + 1, "stopped": "no option"})
            break
        a0, a1 = rng.choice(ops)
        S2 = M.apply(S, n, a0, a1)
        cost = len(S2) - len(S)
        S, n = S2, n + 1
        tr.append({**reading(S, n), "kind": "fill" if cost == 0 else "sub", "options": len(ops)})
    return tr
