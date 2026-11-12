"""Exact least bonds on patterns whose knots each lie within four consecutive distinctions (frozen library of
RANDOM-FATES-20261112-001C-E001; contract.json beside this file).

A bond is an inclusion-minimal constrained set of distinctions under the not-all-equal law (NAE). For two distinctions i < j,
least_bond(i, j) is the size of the smallest bond containing both, or None when there is none among sets chosen inside
[i - margin, j + margin]. The method is a dynamic programme over positions, from the advisor model's design (2026-11-12):
the window state after position m is (x_{m-2}, x_{m-1}, x_m), and a partial choice of S carries
  F  the family of reachable window-state sets over every pattern on the chosen members so far (first member fixed to 0,
     which loses nothing since NAE is complement-closed), and
  G  the same family pooled over every one-member deletion of the chosen members and every pattern on the rest.
Only inclusion-minimal sets are kept (the transitions are monotone). S is constrained exactly when the empty set is in F at the
end, and every S minus one member is free exactly when the empty set is never in G. The rest of the pattern is never cut: every
knot is applied at its last position, and the line runs to its last distinction.
"""

from __future__ import annotations


def make_step(N, knots):
    by = [[] for _ in range(N)]
    for t in knots:
        if max(t) - min(t) > 3:
            raise ValueError("knot not within four consecutive distinctions")
        by[max(t)].append(t)
    trans = []
    for m in range(N):
        tab = [[None, None] for _ in range(8)]
        for s in range(8):
            for x in (0, 1):
                vals = {m - 3: (s >> 2) & 1, m - 2: (s >> 1) & 1, m - 1: s & 1, m: x}
                ok = all(len({vals[v] for v in t}) == 2 for t in by[m])
                tab[s][x] = (((s << 1) & 7) | x) if ok else None
        trans.append(tab)
    cache = {}

    def step(R, m, xs):
        key = (R, m, xs)
        r = cache.get(key)
        if r is not None:
            return r
        out = 0
        for s in range(8):
            if R >> s & 1:
                for x in xs:
                    ns = trans[m][s][x]
                    if ns is not None:
                        out |= 1 << ns
        cache[key] = out
        return out

    return step


def minimal(fam):
    fam = set(fam)
    if 0 in fam:
        return frozenset([0])
    return frozenset(a for a in fam if not any(b != a and (b & a) == b for b in fam))


def least_bond(N, knots, i, j, margin=8, cap=None, max_states=20000, step=None):
    """(size, members, status): status 'ok', 'none' (no bond with members in the margin window) or 'blowup'."""
    if step is None:
        step = make_step(N, knots)
    lo, hi = max(0, i - margin), min(N - 1, j + margin)
    layer = {(frozenset([255]), frozenset()): (0, ())}
    for m in range(N):
        nxt = {}

        def put(Fm, Gm, c, S):
            if 0 in Gm:
                return
            key = (Fm, Gm)
            old = nxt.get(key)
            if old is None or old[0] > c:
                nxt[key] = (c, S)

        must = m == i or m == j
        for (Fm, Gm), (c, S) in layer.items():
            if not must:
                put(minimal(step(R, m, (0, 1)) for R in Fm), minimal(step(R, m, (0, 1)) for R in Gm), c, S)
            if (must or lo <= m <= hi) and (cap is None or c + 1 <= cap) and 0 not in Fm:
                if not Gm:
                    F2 = minimal([step(R, m, (0,)) for R in Fm])
                    G2 = minimal([step(R, m, (0, 1)) for R in Fm])
                else:
                    F2 = minimal([step(R, m, (x,)) for R in Fm for x in (0, 1)])
                    G2 = minimal([step(R, m, (x,)) for R in Gm for x in (0, 1)] + [step(R, m, (0, 1)) for R in Fm])
                put(F2, G2, c + 1, S + (m,))
        layer = nxt
        if len(layer) > max_states:
            return None, None, "blowup"
    best = min(((c, S) for (Fm, Gm), (c, S) in layer.items() if 0 in Fm), default=None)
    if best is None:
        return None, None, "none"
    return best[0], list(best[1]), "ok"
