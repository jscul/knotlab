"""The description language of SHORT-DESC-20261112-001: straight-line macros over three-place knots, a prefix-free code, and exact
evaluation of what a macro allows on its ports.

A description is a list of definitions D_0 .. D_{r-1}; the last is the main one. Definition i has k >= 3 ports (formals), l >= 0 own
distinctions (locals) and c >= 1 calls. A call names K (one knot of the not-all-equal law on three of the definition's k + l
distinctions), an earlier definition D_j (on k_j distinct ones), or, in a definition with three ports, SELF: the definition itself,
so that a knot holds the definition's pattern inside it. A description with SELF also names a depth t >= 1: at depth 1 every SELF
is a knot, at depth t every SELF is the definition at depth t - 1. Shared arguments are how one distinction meets many knots.

Code: counts by Elias gamma (r, k - 2, l + 1, c, t); a callee by a uniform choice among those allowed; arguments by a uniform choice
of an ordered tuple of distinct distinctions. Length = the bits used. The weighting: a description has probability 2^-length
(fair coins), a pattern the sum over the descriptions that expand to it; caps (VARIANTS) truncate it, and each rejection is counted.
"""
import math
import numpy as np

VARIANTS = {
    "main":   dict(arity_cap=6, self_ok=True),
    "wide":   dict(arity_cap=8, self_ok=True),
    "noself": dict(arity_cap=6, self_ok=False),
}
DEF_CAP, LOCAL_CAP, CALL_CAP, T_CAP, KNOT_CAP = 6, 6, 12, 6, 3000

NAE = np.array([s not in (0, 7) for s in range(8)])
TOP = np.ones(8, bool)


def gamma(rng):
    """Elias gamma: n >= 1 with probability 2^-(2 floor(log2 n) + 1). Returns (n, bits)."""
    z = 0
    while rng.random() < 0.5:
        z += 1
    n = 1
    for _ in range(z):
        n = 2 * n + (rng.random() < 0.5)
    return n, 2 * z + 1


def sample(rng, arity_cap, self_ok):
    """One description by fair coins. Returns dict(defs, t, bits, tbits) or dict(reject=cause, bits).
    t is None (and tbits 0) when no SELF is used; with SELF, a depth over T_CAP gives reject='depth' but keeps the definitions
    (the family) for the nested census."""
    bits = 0
    r, b = gamma(rng); bits += b
    if r > DEF_CAP:
        return dict(reject="defs", bits=bits)
    defs = []
    for i in range(r):
        km2, b = gamma(rng); bits += b
        if km2 + 2 > arity_cap:
            return dict(reject="arity", bits=bits)
        k = km2 + 2
        l1, b = gamma(rng); bits += b
        if l1 - 1 > LOCAL_CAP:
            return dict(reject="locals", bits=bits)
        l = l1 - 1
        c, b = gamma(rng); bits += b
        if c > CALL_CAP:
            return dict(reject="calls", bits=bits)
        V = k + l
        options = ["K"] + list(range(i)) + (["SELF"] if self_ok and k == 3 else [])
        calls = []
        for _ in range(c):
            callee = options[rng.randrange(len(options))]; bits += math.log2(len(options))
            ar = 3 if callee in ("K", "SELF") else defs[callee][0]
            if ar > V:
                return dict(reject="args", bits=bits)
            calls.append((callee, tuple(rng.sample(range(V), ar)))); bits += math.log2(math.perm(V, ar))
        defs.append((k, l, calls))
    nested = any(cl == "SELF" for d in defs for cl, _ in d[2])
    if not nested:
        return dict(defs=defs, t=None, bits=bits, tbits=0)
    t, b = gamma(rng)
    out = dict(defs=defs, t=t, bits=bits + b, tbits=b)
    if t > T_CAP:
        out["reject"] = "depth"
    return out


def expand(defs, t, knot_cap=KNOT_CAP):
    """The pattern at depth t: (n, sorted knots) on the distinctions used, or None past knot_cap."""
    knots, nv = set(), [0]

    def call(i, actual, depth):
        k, l, calls = defs[i]
        env = list(actual) + list(range(nv[0], nv[0] + l))
        nv[0] += l
        for callee, args in calls:
            a = [env[x] for x in args]
            if callee == "K" or (callee == "SELF" and depth <= 1):
                knots.add(tuple(sorted(a)))
                if len(knots) > knot_cap:
                    raise OverflowError
            elif callee == "SELF":
                call(i, a, depth - 1)
            else:
                call(callee, a, depth)

    k = defs[-1][0]
    nv[0] = k
    try:
        call(len(defs) - 1, list(range(k)), t or 1)
    except OverflowError:
        return None
    used = sorted({v for e in knots for v in e})
    idx = {v: j for j, v in enumerate(used)}
    return len(used), sorted(tuple(sorted(idx[v] for v in e)) for e in knots)


_ASSIGN = {}


def _assign(V):
    if V not in _ASSIGN:
        _ASSIGN[V] = (np.arange(2 ** V)[:, None] >> np.arange(V)) & 1
    return _ASSIGN[V]


def relations(defs, prev_self):
    """What each definition allows on its ports, given the relation used for its SELF calls (prev_self[i]). Exact: all
    assignments of a definition's k + l distinctions are enumerated. Relation = boolean array over 2^k port states (bit j = port j)."""
    rels = []
    for i, (k, l, calls) in enumerate(defs):
        V = k + l
        A = _assign(V)
        ok = np.ones(2 ** V, bool)
        for callee, args in calls:
            R = NAE if callee == "K" else (prev_self[i] if callee == "SELF" else rels[callee])
            idx = (A[:, list(args)] << np.arange(len(args))).sum(1)
            ok &= R[idx]
        rel = np.zeros(2 ** k, bool)
        rel[np.arange(2 ** V)[ok] & (2 ** k - 1)] = True
        rels.append(rel)
    return rels


def depth_sequence(defs, start):
    """Iterate depths from SELF = start (NAE: the finite descriptions; TOP: the infinite limit, by compactness). Returns
    (alive per depth up to the first repeat of the SELF relations, index where the cycle starts, final SELF relations)."""
    selfs = [i for i, d in enumerate(defs) if any(cl == "SELF" for cl, _ in d[2])]
    prev = {i: start for i in selfs}
    seen, alive = {}, []
    while True:
        rels = relations(defs, prev)
        alive.append(bool(rels[-1].any()))
        key = tuple(rels[i].tobytes() for i in selfs)
        if key in seen:
            return alive, seen[key], {i: rels[i] for i in selfs}
        seen[key] = len(alive) - 1
        prev = {i: rels[i] for i in selfs}


def knot_test(rel):
    """K1-K3 on a three-port relation: constrained as a whole, unconstrained after forgetting any one port, some state allowed."""
    S = [s for s in range(8) if rel[s]]
    if not S or len(S) == 8:
        return False
    for drop in range(3):
        keep = [j for j in range(3) if j != drop]
        if len({tuple((s >> j) & 1 for j in keep) for s in S}) < 4:
            return False
    return True


def fate(defs):
    """The nested family's fate over depth t = 1, 2, ...: 'at once' (no state at depth 1), 'a while' (first none at depth T >= 2),
    'forever' (a state at every depth), always by the first death; with the infinite limit's verdict and the kind of each SELF definition's limit relation."""
    alive, c0, _ = depth_sequence(defs, NAE)
    # alive[j] is depth j + 1; depths from c0 + 1 on repeat with period len(alive) - 1 - c0
    first_dead = next((j + 1 for j, a in enumerate(alive) if not a), None)
    if first_dead is None:
        f = "forever"
    elif first_dead == 1:
        f = "at once"
    else:
        f = "a while"
    lim_alive, _, lim = depth_sequence(defs, TOP)
    kinds = []
    for rel in lim.values():
        pairs = int(rel.sum()) // 2
        kinds.append("knot" if knot_test(rel) else {0: "none", 1: "three tied", 2: "two tied", 4: "free"}.get(pairs, "other"))
    # after a first death: 'recurrent' when the repeating cycle of depths still holds a living one, else 'stays dead'
    after = None if first_dead is None else ("recurrent" if any(alive[c0 + 1:]) else "stays dead")
    return dict(fate=f, first_dead=first_dead, period=len(alive) - 1 - c0, revives=bool(first_dead) and any(alive[first_dead:]),
                after=after,
                limit_alive=lim_alive[-1], limit_kinds=kinds, depths_read=len(alive))
