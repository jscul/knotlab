"""MEET-ORDERS-20261118-001B: exact engine for KF3 and the presentations of a line.

KF3 (STATE-RULES-20261117-001, KNOT-CAP-20261117-001): add distinction p = n with an irredundant set of 1..3 betweenness knots,
each on p and two old distinctions that already share a knot; every old state extends; p constrained and not a copy; fewest
resulting states; uniform over the qualifying knot sets.  Written fresh for this study, following the move semantics of
KNOT-CAP's referee code (research/KNOT-CAP-20261117-001/referee-R1/referee_cap.py), which checks.py compares against.

State: (S, G) with S the allowed states (bitmasks over distinctions 0..n-1) and G the pairs that share a knot.
The rule reads K only through G, so (S, G) is an exact Markov state.  Classes are merged under renaming
(canonical form by individualisation-refinement on the disagreement counts and G, exhaustive over the search tree).

Presentations of the line 0..m (m = n - 1) by n - 2 knots are bracketings: knot (a, c, b) with a < c < b splits the steps
a+1..b at c; the top knot is (0, c, m).
"""
import itertools
from collections import defaultdict, Counter
from fractions import Fraction
import numpy as np
import networkx as nx


def pc(x):
    return bin(x).count("1")


def ok_btw(s, x, y, z):
    return not ((((s >> x) ^ (s >> z)) & 1) == 0 and (((s >> x) ^ (s >> y)) & 1) == 1)


def base(n, knots):
    return tuple(s for s in range(1 << n) if all(ok_btw(s, *k) for k in knots))


def pairs_of(knots):
    return frozenset((min(a, b), max(a, b)) for k in knots for a, b in itertools.combinations(k, 2))


def cols(S, n):
    O = [0] * n
    for i, s in enumerate(S):
        for u in range(n):
            if (s >> u) & 1:
                O[u] |= 1 << i
    full = (1 << len(S)) - 1
    return O, [full ^ o for o in O], full


def candidates(S, n, G):
    """Each knot-local knot on the new distinction p = n as (knot, pin0 mask, pin1 mask) over states."""
    O, Z, full = cols(S, n)
    p = n
    out = []
    for (u, v) in sorted(G):
        eq = (O[u] & O[v]) | (Z[u] & Z[v])
        ne = full ^ eq
        # B(u, p, v): where u = v, p = u
        out.append(((u, p, v), Z[u] & Z[v], O[u] & O[v]))
        # B(u, v, p): v between u and p: where u != v, p = v
        out.append(((u, v, p), ne & Z[v], ne & O[v]))
        # B(v, u, p): where u != v, p = u
        out.append(((v, u, p), ne & Z[u], ne & O[u]))
    return out, O, Z, full


def moves(S, n, G):
    """All admissible irredundant knot sets (1..3 knots): returns list of (a0, a1, knots)."""
    cands, O, Z, full = candidates(S, n, G)
    N = len(S)
    ties = {(Z[u], O[u]) for u in range(n)}
    m = len(cands)
    P0 = np.array([c[1] for c in cands], dtype=np.int64)
    P1 = np.array([c[2] for c in cands], dtype=np.int64)
    comp = ((P0[:, None] & P1[None, :]) == 0) & ((P1[:, None] & P0[None, :]) == 0)
    out = []

    def finish(idx):
        pin0 = 0
        pin1 = 0
        for i in idx:
            pin0 |= cands[i][1]
            pin1 |= cands[i][2]
        if len(idx) >= 2:
            for d in idx:
                q0 = 0
                q1 = 0
                for i in idx:
                    if i != d:
                        q0 |= cands[i][1]
                        q1 |= cands[i][2]
                if q0 == pin0 and q1 == pin1:
                    return None
        a0 = full ^ pin1          # p may be 0 unless pinned to 1
        a1 = full ^ pin0
        if pc(a0) + pc(a1) >= 2 * N:
            return None
        if (a0, a1) in ties:
            return None
        return (a0, a1, tuple(cands[i][0] for i in idx))

    for i in range(m):
        r = finish((i,))
        if r:
            out.append(r)
    ii, jj = np.nonzero(np.triu(comp, 1))
    for i, j in zip(ii.tolist(), jj.tolist()):
        r = finish((i, j))
        if r:
            out.append(r)
        ks = np.nonzero(comp[i, j + 1:] & comp[j, j + 1:])[0] + j + 1
        for k in ks.tolist():
            r = finish((i, j, k))
            if r:
                out.append(r)
    return out


def apply(S, n, a0, a1):
    out = []
    for i, s in enumerate(S):
        if (a0 >> i) & 1:
            out.append(s)
        if (a1 >> i) & 1:
            out.append(s | (1 << n))
    return tuple(sorted(out))


def dmat(S, n):
    return [[sum(((s >> u) ^ (s >> v)) & 1 for s in S) for v in range(n)] for u in range(n)]


def canon(S, n, G):
    """Canonical form of (S, G) under renaming, by individualisation-refinement (exhaustive over the search tree)."""
    D = dmat(S, n)
    A = [[0] * n for _ in range(n)]
    for u, v in G:
        A[u][v] = A[v][u] = 1

    def refine(col):
        while True:
            sig = [(col[u], tuple(sorted((D[u][v], A[u][v], col[v]) for v in range(n) if v != u))) for u in range(n)]
            keys = sorted(set(sig))
            new = [keys.index(sig[u]) for u in range(n)]
            if len(set(new)) == len(set(col)):
                return new
            col = new

    best = [None]

    def cert(order):
        pos = {u: i for i, u in enumerate(order)}
        st = tuple(sorted(sum(1 << pos[u] for u in range(n) if (s >> u) & 1) for s in S))
        ge = tuple(sorted((min(pos[u], pos[v]), max(pos[u], pos[v])) for u, v in G))
        return (st, ge)

    def search(col):
        col = refine(col)
        if len(set(col)) == n:
            order = sorted(range(n), key=lambda u: col[u])
            c = cert(order)
            if best[0] is None or c < best[0]:
                best[0] = c
            return
        cnt = Counter(col)
        # first smallest non-singleton cell
        target = min((cnt[c], c) for c in cnt if cnt[c] > 1)[1]
        for u in range(n):
            if col[u] == target:
                c2 = [2 * x for x in col]
                c2[u] = 2 * target - 1
                search(c2)

    search([0] * n)
    st, ge = best[0]
    return st, frozenset(ge)


def measure(S, n):
    full = (1 << n) - 1
    sp = sorted({min(s, full ^ s) for s in S if s not in (0, full)})
    cr = [(i, j) for i, j in itertools.combinations(range(len(sp)), 2)
          if all(x for x in (sp[i] & sp[j], sp[i] & (full ^ sp[j]), (full ^ sp[i]) & sp[j], (full ^ sp[i]) & (full ^ sp[j])))]
    Gc = nx.Graph()
    Gc.add_nodes_from(range(len(sp)))
    Gc.add_edges_from(cr)
    if not cr:
        k = 1
    elif nx.is_bipartite(Gc):
        k = 2
    else:
        k = 3
    H = nx.Graph()
    sides = [(i, x) for i, a in enumerate(sp) for x in (a, full ^ a)]
    H.add_nodes_from(range(len(sides)))
    for a, b in itertools.combinations(range(len(sides)), 2):
        if sides[a][0] != sides[b][0] and (sides[a][1] | sides[b][1]) == full:
            H.add_edge(a, b)
    lam = len(sp) - len(nx.max_weight_matching(H, maxcardinality=True))
    return {"N": len(S), "splits": len(sp), "crossings": len(cr), "k": k, "lam": lam}


def step_dist(S, n, G):
    """KF3 step: dict {(S', G'): prob} (labelled), or None if stalled."""
    mv = moves(S, n, G)
    if not mv:
        return None
    low = min(pc(a0) + pc(a1) for a0, a1, _ in mv)
    top = [x for x in mv if pc(x[0]) + pc(x[1]) == low]
    out = defaultdict(Fraction)
    for a0, a1, ks in top:
        S2 = apply(S, n, a0, a1)
        G2 = G | pairs_of(ks)
        out[(S2, G2)] += Fraction(1, len(top))
    return out


def exact(n, knots, nmax, use_canon=True, verbose=False):
    S = base(n, knots)
    G = pairs_of(knots)
    key = canon(S, n, G) if use_canon else (S, G)
    dist = {key: Fraction(1)}
    levels = []
    stalled = Fraction(0)
    while True:
        lam = Counter()
        two = Fraction(0)
        for (S1, G1), p in dist.items():
            m = measure(S1, n)
            lam[m["lam"]] += p
            if m["k"] == 2 and m["lam"] == 2:
                two += p
        levels.append({"n": n, "classes": len(dist), "two": two, "lam": dict(lam), "stalled": stalled, "dist": dist})
        if verbose:
            print(n, len(dist), two, flush=True)
        if n >= nmax:
            break
        new = defaultdict(Fraction)
        for (S1, G1), p in dist.items():
            sd = step_dist(S1, n, G1)
            if sd is None:
                stalled += p
                continue
            for (S2, G2), q in sd.items():
                k2 = canon(S2, n + 1, G2) if use_canon else (S2, G2)
                new[k2] += p * q
        dist = dict(new)
        n += 1
    return levels


# ---------------------------------------------------------------- presentations of a line and their nesting

def bracketings(a, b):
    """Every set of knots (x, c, y), x < c < y, bracketing the steps a+1..b (the literature's triangulations of the polygon a..b)."""
    if b - a <= 1:
        return [[]]
    out = []
    for c in range(a + 1, b):
        for L in bracketings(a, c):
            for R in bracketings(c, b):
                out.append([(a, c, b)] + L + R)
    return out


def nesting(knots, a, b, ordered=False):
    """The nesting of the knots on [a, b] as a bracket string: 'x' for a step, '(L,R)' for a knot; without order the two parts
    are sorted (the literature's unlabelled rooted binary tree)."""
    span = {(k[0], k[2]): k for k in knots}
    if (a, b) not in span:
        return "x"
    c = span[(a, b)][1]
    L, R = nesting(knots, a, c, ordered), nesting(knots, c, b, ordered)
    return "(" + ",".join([L, R] if ordered else sorted([L, R])) + ")"


def mirror(knots, m):
    return sorted((m - k[2], m - k[1], m - k[0]) for k in knots)


def relations(knots):
    """parent, children, within (descendants) and holders (ancestors) of each knot of a bracketing."""
    span = {(k[0], k[2]): k for k in knots}
    children = {k: [span[s] for s in ((k[0], k[1]), (k[1], k[2])) if s in span] for k in knots}
    parent = {}
    for k in knots:
        for ch in children[k]:
            parent[ch] = k

    def below(k):
        out = set()
        for ch in children[k]:
            out |= {ch} | below(ch)
        return out
    within = {k: below(k) for k in knots}
    holders = {k: {j for j in knots if k in within[j]} for k in knots}
    return parent, children, within, holders


def formula(knots):
    """Theorem 1: the chance of two orders after the second new distinction under KF3 from the presentation."""
    n0 = len(knots) + 2
    parent, children, within, holders = relations(knots)
    tot = Fraction(0)
    for k in knots:
        inc = len(knots) - 1 - len(within[k]) - len(holders[k])
        p = 1 if k in parent else 0
        c = len(children[k])
        tot += Fraction(inc + 2 * p + c, (n0 - 3) + 2 * (p + c))
    return tot / len(knots)


def chain_formula(n0):
    """Theorem 1 for a chain of knots (each knot directly within the next)."""
    return (Fraction(3, n0 - 1) + Fraction(3 * (n0 - 4), n0 + 1)) / (n0 - 2)


def two_orders(m):
    return m["k"] == 2 and m["lam"] == 2


def zero_cost_top(S, n, G):
    """KF3's options at (S, G): the fewest-states knot sets, with their cost (added states)."""
    mv = moves(S, n, G)
    low = min(pc(a0) + pc(a1) for a0, a1, _ in mv)
    return low - len(S), [x for x in mv if pc(x[0]) + pc(x[1]) == low]


def old_pairs(ks, new):
    return frozenset(tuple(sorted(set(k) - {new})) for k in ks)


def odd_sets(S, n, n0):
    """Exploratory X.  While every step so far added no state, each new distinction is a function of the line's cut, the parity
    of an odd set of line distinctions (its odd set: the line positions where its value changes along the cuts).  Returns the
    odd sets of the new distinctions, or None once a step has added a state."""
    m = n0 - 1
    low = (1 << n0) - 1
    ext = {}
    for s in S:
        ext.setdefault(s & low, []).append(s)
    prefixes = [0] + [(1 << k) - 1 for k in range(1, m + 1)] + [low]
    if len(S) != 2 * n0 or any(len(ext.get(P, [])) != 1 for P in prefixes):
        return None
    out = []
    for u in range(n0, n):
        f = [(ext[P][0] >> u) & 1 for P in prefixes]
        out.append(tuple(i for i in range(n0) if f[i] != f[i + 1]))
    return out


def classify_second_step(knots, first):
    """Lemma B's finite check for one presentation and one first knot.  Returns a dict with the second step's options,
    each classified as F (the fill of another knot) or E (two pairs of a knot sharing a pair with the first, plus one pair
    holding the first new distinction q), the verdicts, and the checks of the lemma."""
    n0 = len(knots) + 2
    m = n0 - 1
    S0 = base(n0, knots)
    G0 = pairs_of(knots)
    cost0, top0 = zero_cost_top(S0, n0, G0)
    q = n0
    fills = {}
    for a0, a1, ks in top0:
        used = old_pairs(ks, q)
        hit = [k for k in knots if used == pairs_of([k])]
        assert cost0 == 0 and len(hit) == 1, ("first step", knots, ks)
        fills.setdefault(hit[0], []).append((a0, a1, ks))
    assert sorted(fills) == sorted(knots) and all(len(v) == 1 for v in fills.values()), ("first step", knots)
    a0, a1, ks = fills[first][0]
    S1 = apply(S0, n0, a0, a1)
    G1 = G0 | pairs_of(ks)
    cost1, top1 = zero_cost_top(S1, n0 + 1, G1)
    parent, children, within, holders = relations(knots)
    kp = pairs_of([first])
    neigh = ([parent[first]] if first in parent else []) + children[first]
    r = n0 + 1
    rows = []
    for b0, b1, ks2 in top1:
        used = old_pairs(ks2, r)
        S2 = apply(S1, n0 + 1, b0, b1)
        verdict = two_orders(measure(S2, n0 + 2))
        qpairs = frozenset(p for p in used if q in p)
        lpairs = used - qpairs
        kind, at = "other", None
        if not qpairs:
            hit = [k for k in knots if k != first and lpairs == pairs_of([k])]
            if hit:
                kind, at = "F", hit[0]
        elif len(qpairs) == 1:
            for nu in neigh:
                if lpairs == pairs_of([nu]) - kp:
                    kind, at = "E", nu
        odd = odd_sets(S2, n0 + 2, n0)
        rows.append({"kind": kind, "at": at, "two": verdict, "knots": ks2, "odd": odd[-1] if odd else None, "q": odd[0] if odd else None})
    ok = cost1 == 0
    F = [x for x in rows if x["kind"] == "F"]
    E = [x for x in rows if x["kind"] == "E"]
    ok &= not [x for x in rows if x["kind"] == "other"]
    ok &= sorted(x["at"] for x in F) == sorted(k for k in knots if k != first)
    for x in rows:
        ok &= x["q"] == tuple(first)
    for x in F:
        apart = x["at"] not in within[first] and x["at"] not in holders[first]
        ok &= x["two"] == apart and x["odd"] == tuple(x["at"])
    for nu in neigh:
        e = [x for x in E if x["at"] == nu]
        good = sum(x["two"] for x in e)
        ok &= len(e) == 2 and good == (2 if first in parent and nu == parent[first] else 1)
        shared = sorted(set(first) & set(nu))
        x_, y_ = (set(first) - set(shared)).pop(), (set(nu) - set(shared)).pop()
        ok &= sorted(t["odd"] for t in e) == sorted(tuple(sorted((x_, y_, s))) for s in shared)
    good = sum(x["two"] for x in rows)
    return {"ok": bool(ok), "options": len(rows), "good": good, "cost": cost1, "rows": rows}


def order_dist(levels):
    """Readable per-level distributions of the number of orders from exact()."""
    out = []
    for L in levels:
        out.append({"n": L["n"], "classes": L["classes"], "two": str(L["two"]),
                    "lam": {str(k): str(v) for k, v in sorted(L["lam"].items())}, "stalled": str(L["stalled"])})
    return out
