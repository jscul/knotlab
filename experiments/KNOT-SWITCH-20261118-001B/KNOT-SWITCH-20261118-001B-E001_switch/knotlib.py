"""KNOT-SWITCH-20261118-001B-E001: what state of the knots SEED's "no two splits cross" reads.

The knot complex K of a base with its knots: vertices the distinctions, edges the co-knotted pairs, triangles the knots (as
unordered triples).  Its homology is over GF(2).  Runs use KF3's knot-local moves (melib.py through nnlib.py, both pinned) and
record every knot, so K is known at every step.  Rules: KF3, NN, NN2 (NEVER-NEST-20261118-001) and SEEDK, PICK-TWO-20261118-001's
SEED with knot-local moves and its switch read from the knots (b2(K) = 0) instead of from the crossings.
"""
import itertools
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.append(os.path.join(ROOT, "experiments", "PICK-TWO-20261118-001B", "PICK-TWO-20261118-001B-E001_pick"))
import picklib as P  # noqa: E402

L, M = P.L, P.M


def complex_of(n, knots):
    """Vertices, edges (co-knotted pairs) and triangles (distinct triples) of the knot complex."""
    T = sorted({tuple(sorted(k)) for k in knots})
    E = sorted({(a, b) for t in T for a, b in itertools.combinations(t, 2)})
    return list(range(n)), E, T


def rank_gf2(rows):
    """Rank over GF(2) of a list of int bitmasks."""
    basis = {}
    r = 0
    for x in rows:
        while x:
            h = x.bit_length() - 1
            if h in basis:
                x ^= basis[h]
            else:
                basis[h] = x
                r += 1
                break
    return r


def betti(n, knots):
    V, E, T = complex_of(n, knots)
    eidx = {e: i for i, e in enumerate(E)}
    d2 = [sum(1 << eidx[(a, b)] for a, b in itertools.combinations(t, 2)) for t in T]
    r2 = rank_gf2(d2)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for a, b in E:
        parent[find(a)] = find(b)
    used = {v for e in E for v in e}
    b0 = len({find(v) for v in used}) + (n - len(used))
    b1 = len(E) - (n - b0) - r2
    b2 = len(T) - r2
    return {"b0": b0, "b1": b1, "b2": b2, "edges": len(E), "triangles": len(T),
            "duplicate_knots": len(knots) - len({tuple(sorted(k)) for k in knots})}


def filled_knots(knots):
    """The filled knots: four distinctions carrying four knots, each of the four the middle of exactly one (a knot with the three
    knots of its fill).  Returns the four-sets (sorted tuples)."""
    by = {}
    for k in knots:
        by.setdefault(tuple(sorted(k)), set()).add(k[1])
    out = set()
    T = list(by)
    adj = {}
    for t in T:
        for v in t:
            adj.setdefault(v, set()).update(t)
    for t in T:
        for w in set.intersection(*(adj[v] for v in t)) - set(t):
            four = tuple(sorted(t + (w,)))
            if four in out:
                continue
            trip = [tuple(sorted(x)) for x in itertools.combinations(four, 3)]
            if not all(x in by for x in trip):
                continue
            # choose one middle per triple so that each of the four distinctions is a middle exactly once
            options = [[m for m in by[x]] for x in trip]
            if any(sorted(c) == list(four) for c in itertools.product(*options)):
                out.add(four)
    return sorted(out)


def other_readings(n, knots):
    """(i) the most knots (distinct triples) on one pair; (ii) whether some four distinctions have all four triples knotted;
    (ii') the number of filled knots."""
    T = {tuple(sorted(k)) for k in knots}
    per_pair = {}
    for t in T:
        for e in itertools.combinations(t, 2):
            per_pair[e] = per_pair.get(e, 0) + 1
    four = False
    verts = sorted({v for t in T for v in t})
    adj = {}
    for t in T:
        for v in t:
            adj.setdefault(v, set()).update(t)
    for t in T:
        for w in set.intersection(*(adj[v] for v in t)) - set(t):
            if all(tuple(sorted(s)) in T for s in itertools.combinations(t + (w,), 3)):
                four = True
                break
        if four:
            break
    return {"max_knots_per_pair": max(per_pair.values()) if per_pair else 0, "full_four": four,
            "filled_knots": len(filled_knots(knots))}


def nothing_crosses(S, n):
    sp, G = P.crossing_graph(S, n)
    return G.number_of_edges() == 0


def cyc(pairs):
    """Whether the graph of these pairs has a cycle (|E| > |V| - components)."""
    pairs = set(pairs)
    vs = {v for e in pairs for v in e}
    parent = {v: v for v in vs}

    def find(x):
        while parent[x] != x:
            x = parent[x]
        return x
    comps = len(vs)
    for a, b in pairs:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
            comps -= 1
    return len(pairs) > len(vs) - comps


def components(pairs):
    pairs = set(pairs)
    vs = {v for e in pairs for v in e}
    parent = {v: v for v in vs}

    def find(x):
        while parent[x] != x:
            x = parent[x]
        return x
    for a, b in pairs:
        parent[find(a)] = find(b)
    return len({find(v) for v in vs})


def seedk_options(S, n, G, b2):
    """SEEDK's options (a list of (a0, a1, knots), uniform over knot sets): any KF3 fill while b2 = 0; afterwards the fills that
    make no new crossing between two splits that already crossed something, and under which a split that crossed nothing and gains
    crossings ends with exactly the crossers of a split that already crossed something; else a knot-local subdivision."""
    mv = L.moves(S, n, G)
    N = len(S)
    zero = [x for x in mv if P.pc(x[0]) + P.pc(x[1]) == N]
    if b2 == 0:
        good = zero
    else:
        good = []
        memo = {}
        for x in zero:
            key = x[:2]
            if key not in memo:
                new, Gc = P.new_crossings(S, n, x[1])
                active = {v for v in Gc if Gc.degree(v) > 0}
                ok = all(not (i in active and j in active) for i, j in new)
                if ok and new:
                    H = Gc.copy()
                    H.add_edges_from(new)
                    gained = {v for e in new for v in e if v not in active}
                    nb = {v: frozenset(H[v]) for v in H}
                    old = {nb[v] for v in active}
                    ok = all(nb[u] in old for u in gained)
                memo[key] = ok
            if memo[key]:
                good.append(x)
    if good:
        return good, "fill"
    return [x for x in mv if L.is_sub(x[2], n, S)], "sub"


def grow(knots0, n0, nmax, rule, seed_value):
    """A labelled run of a knot-local rule, recording every knot and the readings at every step."""
    rng = random.Random(seed_value)
    S = M.base(n0, knots0)
    G = M.pairs_of(knots0)
    knots = list(knots0)
    n = n0
    trace = []

    def row(kind, pairs=None, extra=None):
        b = betti(n, knots)
        o = other_readings(n, knots)
        k, lam = P.kl(S, n)
        r = {"n": n, "N": len(S), "k": k, "lam": lam, "kind": kind, "nothing_crosses": nothing_crosses(S, n),
             "full_grid": P.grid(S, n) is not None, **b, **o}
        if pairs is not None:
            r["pair_graph_cycle"] = cyc(pairs)
            r["pairs_used"] = len(set(pairs))
            r["pair_vertices"] = len({v for e in pairs for v in e})
            r["pair_components"] = components(pairs)
        if extra:
            r.update(extra)
        trace.append(r)
    row("start")
    while n < nmax:
        if len(S) > 60:
            trace.append({"n": n + 1, "stopped": "state limit"})
            break
        b2 = trace[-1]["b2"]
        extra = {}
        if rule == "SEEDK":
            ops, kind = seedk_options(S, n, G, b2)
            extra["switch_by_knots"] = b2 == 0
            extra["switch_by_crossings"] = trace[-1]["nothing_crosses"]
        else:
            ops, info = L.options(S, n, G, rule)
        if not ops:
            trace.append({"n": n + 1, "stopped": "no option"})
            break
        a0, a1, ks = rng.choice(ops)
        S2 = M.apply(S, n, a0, a1)
        pairs = [tuple(sorted(x for x in k if x != n)) for k in ks]
        kind = "fill" if len(S2) == len(S) else ("sub" if L.is_sub(ks, n, S) else "other")
        G = G | M.pairs_of(ks)
        knots += list(ks)
        S, n = S2, n + 1
        row(kind, pairs, extra)
    return trace
