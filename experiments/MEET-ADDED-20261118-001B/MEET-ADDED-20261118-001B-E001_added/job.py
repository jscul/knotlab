"""MEET-ADDED-20261118-001B frozen run, for the shared runner (docs/tooling/shared-runner.md).

melib.py is MEET-ORDERS-20261118-001B's engine, copied unchanged (same sha256).

Case A|n0|d|i: labelled KF3 from bracketing i of the line of n0 (every bracketing, prior uniform over labelled presentations),
tracking the knots each step adds (as betweenness knots with their middles), to n0 + d. At every level, the law of the grown base
read with every distinction anonymous (up to renaming, which includes the line's reversal) in these arms:
  P0  the added pairs alone, as a graph on the n distinctions, no states (the referee's preview);
  U   the states alone;
  P1  the states with the added pairs (pairs that hold a new distinction);
  T1  the states with the added knots as triples (their distinctions, no middles);
  K1  the states with the added knots and their rules (middles marked);
  SG  the states with every co-knotted pair, the starting ones too (a sanity ceiling);
and N, all named (the line's distinctions by place up to reversal, the new ones by order of growth), with the joint laws of
(arm, N) for the conditional entropy of the named base given each arm.
"""
import hashlib
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import melib as M

CASES = [(5, 4), (6, 4), (7, 3)]
ARMS = ("P0", "U", "P1", "T1", "K1", "SG")


def cases():
    for n0, d in CASES:
        for i, T in enumerate(M.bracketings(0, n0 - 1)):
            yield f"A|{n0}|{d}|{i}", {"n0": n0, "depth": d, "knots": T}


def norm_knot(k):
    x, y, z = k
    return (min(x, z), y, max(x, z))


def exact_with_knots(n0, T, depth):
    """Labelled KF3 keyed by (states, added knots); the co-knotted pairs are the starting ones and the added knots' pairs."""
    G0 = M.pairs_of(T)
    dist = {(M.base(n0, T), frozenset()): Fraction(1)}
    levels = [dict(dist)]
    n = n0
    for _ in range(depth):
        new = defaultdict(Fraction)
        for (S, K), p in dist.items():
            G = G0 | M.pairs_of(list(K))
            mv = M.moves(S, n, G)
            low = min(M.pc(a0) + M.pc(a1) for a0, a1, _ in mv)
            top = [x for x in mv if M.pc(x[0]) + M.pc(x[1]) == low]
            for a0, a1, ks in top:
                new[(M.apply(S, n, a0, a1), K | frozenset(norm_knot(k) for k in ks))] += p / len(top)
        dist = dict(new)
        n += 1
        levels.append(dist)
    return levels


def canon_struct(S, n, pairs=(), triples=(), knots=(), use_states=True):
    """Canonical form of (states, pairs, triples, knots) under renaming, by individualisation-refinement with an exhaustive search
    and a certificate holding every relabelled part."""
    D = M.dmat(S, n) if use_states else [[0] * n for _ in range(n)]
    E = {frozenset(p) for p in pairs}
    tri = Counter()
    for t in triples:
        for a in t:
            for b in t:
                if a != b:
                    tri[(a, b)] += 1
    mid_end = Counter()
    mids = Counter()
    for (a, c, b) in knots:
        mids[c] += 1
        mid_end[(c, a)] += 1
        mid_end[(c, b)] += 1
    W = [[(D[u][v], frozenset((u, v)) in E, tri[(u, v)], mid_end[(u, v)], mid_end[(v, u)]) for v in range(n)] for u in range(n)]

    def refine(col):
        while True:
            sig = [(col[u], mids[u], tuple(sorted((W[u][v], col[v]) for v in range(n) if v != u))) for u in range(n)]
            keys = sorted(set(sig))
            new = [keys.index(x) for x in sig]
            if len(set(new)) == len(set(col)):
                return new
            col = new

    best = [None]

    def cert(order):
        pos = {u: i for i, u in enumerate(order)}
        st = tuple(sorted(sum(1 << pos[u] for u in range(n) if (s >> u) & 1) for s in S)) if use_states else ()
        pe = tuple(sorted(tuple(sorted(pos[u] for u in p)) for p in E))
        tr = tuple(sorted(tuple(sorted(pos[u] for u in t)) for t in triples))
        kn = tuple(sorted((min(pos[a], pos[b]), pos[c], max(pos[a], pos[b])) for (a, c, b) in knots))
        return (st, pe, tr, kn)

    def search(col):
        col = refine(col)
        if len(set(col)) == n:
            c = cert(sorted(range(n), key=lambda u: col[u]))
            if best[0] is None or c < best[0]:
                best[0] = c
            return
        cnt = Counter(col)
        target = min((cnt[c], c) for c in cnt if cnt[c] > 1)[1]
        for u in range(n):
            if col[u] == target:
                c2 = [2 * x for x in col]
                c2[u] = 2 * target - 1
                search(c2)

    search([0] * n)
    return hashlib.sha256(repr(best[0]).encode()).hexdigest()[:20]


def readings(S, K, n, n0, G0):
    added_pairs = [p for p in M.pairs_of(list(K))]
    triples = [frozenset(k) for k in K]
    m = n0 - 1
    mirror = [m - u if u < n0 else u for u in range(n)]
    S_m = tuple(sorted(sum(1 << mirror[u] for u in range(n) if (s >> u) & 1) for s in S))
    return {
        "P0": canon_struct((), n, pairs=added_pairs, use_states=False),
        "U": canon_struct(S, n),
        "P1": canon_struct(S, n, pairs=added_pairs),
        "T1": canon_struct(S, n, triples=triples),
        "K1": canon_struct(S, n, knots=list(K)),
        "SG": canon_struct(S, n, pairs=list(G0) + added_pairs),
        "N": hashlib.sha256(repr(min(S, S_m)).encode()).hexdigest()[:20],
    }


def run(case_id, p):
    n0, d, T = p["n0"], p["depth"], [tuple(k) for k in p["knots"]]
    G0 = M.pairs_of(T)
    levels = []
    for lev, dist in enumerate(exact_with_knots(n0, T, d)):
        n = n0 + lev
        laws = {r: defaultdict(Fraction) for r in ARMS + ("N",) + tuple(a + "|N" for a in ("U", "P1", "T1", "K1"))}
        for (S, K), q in dist.items():
            rd = readings(S, K, n, n0, G0)
            for r in ARMS + ("N",):
                laws[r][rd[r]] += q
            for a in ("U", "P1", "T1", "K1"):
                laws[a + "|N"][rd[a] + ":" + rd["N"]] += q
        levels.append({"n": n, "labelled": len(dist), "laws": {r: {k: str(v) for k, v in sorted(w.items())} for r, w in laws.items()}})
    return {"n0": n0, "depth": d, "knots": T, "bare": M.nesting(T, 0, n0 - 1), "levels": levels}


if __name__ == "__main__":
    print(sum(1 for _ in cases()), "cases")
