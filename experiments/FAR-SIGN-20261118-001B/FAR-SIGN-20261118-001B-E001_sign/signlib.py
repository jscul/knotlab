"""FAR-SIGN-20261118-001B-E001: is the far pair's sign SEED's copy step?

COPY-CLASS-20261118-001's referee found that a crossing-making fill is a copy step (SEED accepts it after its switch) exactly when
some knot set of it, with one middle knot and two end knots of which exactly one touches the middle pair, has its far end pair
separated by every crossed split.  Ticket A proves what that sign decides and gives counterexamples off knot-local fills.  This
library scores, for every crossing-making knot set:
- the sign, the weak sign (r sides with d on every crossed split), the near-pair sign (no crossed split separates the near pair);
- the moved splits (r off p's side) and new crossings, against A's L1 and L2;
- F1 (a fill that gives an uncrossed split a crossing has the sign), T1 (with the sign, no uncrossed split is moved), T2 (with the
  sign, the moved crossed splits are one whole order), and the pair pattern of A's L5;
- the closure picture (COPY-READ's copy class) and the marked five-distinction picture: what p, q, a, c, d see of every split,
  with one mark for crossed.
A knot set is written with r = n: a middle knot (u, n, v) pins r to u where u = v; an end knot (u, v, n) pins r to v where u != v.
"""
import itertools
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.append(os.path.join(ROOT, "experiments", "COPY-CLASS-20261118-001B", "COPY-CLASS-20261118-001B-E001_class"))
import classlib as CL  # noqa: E402

K, M, L, P, KL = CL.K, CL.M, CL.L, CL.P, CL.KL
COPY_CLASS = CL.COPY_CLASS


def shape(ks, n):
    """The roles of a knot set with one middle knot and two end knots, exactly one end pair touching the middle pair:
    {"p": shared, "q", "a", "c", "d", "near_to_shared"}; p is None when the touching end pair meets the middle pair in two places.
    None for any other knot set."""
    mids = [k for k in ks if k[1] == n]
    ends = [k for k in ks if k[1] != n]
    if len(mids) != 1 or len(ends) != 2:
        return None
    mp = {mids[0][0], mids[0][2]}
    pe = [(k[0], k[1]) for k in ends]
    touch = [t for t in range(2) if mp & set(pe[t])]
    if len(touch) != 1:
        return None
    near, far = pe[touch[0]], pe[1 - touch[0]]
    common = mp & set(near)
    out = {"c": far[0], "d": far[1], "near": near, "mid": tuple(sorted(mp))}
    if len(common) != 1:
        out.update({"p": None, "q": None, "a": None, "near_to_shared": None})
        return out
    p = common.pop()
    out.update({"p": p, "q": (mp - {p}).pop(), "a": near[0] if near[1] == p else near[1], "near_to_shared": near[1] == p})
    return out


def sep(s, x, y):
    return ((s >> x) ^ (s >> y)) & 1


def base_view(S, n):
    """Splits, crossing graph, the crossed splits and their two orders (None unless the crossing graph on crossed splits is complete
    bipartite)."""
    sp, Gc = P.crossing_graph(S, n)
    active = {v for v in Gc if Gc.degree(v) > 0}
    orders = None
    if active:
        H = Gc.subgraph(active)
        import networkx as nx
        if nx.is_connected(H) and nx.is_bipartite(H):
            X, Y = nx.bipartite.sets(H)
            if H.number_of_edges() == len(X) * len(Y):
                orders = (frozenset(X), frozenset(Y))
    return sp, Gc, active, orders


def seed_verdict(sp, Gc, active, new):
    """SEED's two clauses from the old crossing graph and the new crossings (a zero-cost fill keeps every split)."""
    if any(i in active and j in active for i, j in new):
        return False, "a"
    nb = {}
    for i, j in new:
        nb.setdefault(i, set()).add(j)
        nb.setdefault(j, set()).add(i)
    gained = [u for u in nb if u not in active]
    after = {v: frozenset(set(Gc[v]) | nb.get(v, set())) for v in Gc}
    olds = {after[m] for m in active}
    return all(after[u] in olds for u in gained), ("b" if not all(after[u] in olds for u in gained) else None)


def trace(s, roles, ref):
    """What the distinctions in roles see of split s: their sides, normalised so that ref's side is 1."""
    flip = 0 if (s >> ref) & 1 else 1
    return tuple(((s >> x) & 1) ^ flip for x in roles)


def analyse(S, n, a1, ks, sp, Gc, active, orders, new, gained):
    """Every reading of one crossing-making knot set (A's lemmas checked where the roles allow)."""
    f = shape(ks, n)
    if f is None:
        return None
    idx = {x: i for i, x in enumerate(S)}
    full = (1 << n) - 1
    rv = lambda s: (a1 >> idx[s]) & 1        # r's value on state s (r on s's 1-side when 1)
    c, d = f["c"], f["d"]
    out = {"near_to_shared": f["near_to_shared"], "two_touch": f["p"] is None,
           "sign": all(sep(sp[i], c, d) for i in active),
           "weak": all(rv(sp[i]) == ((sp[i] >> d) & 1) for i in active)}
    if f["p"] is None:
        return out
    p, q, a = f["p"], f["q"], f["a"]
    out["near_none"] = not any(sep(sp[i], a, p) for i in active)
    if not f["near_to_shared"]:
        return out
    Pside = [s if (s >> p) & 1 else full ^ s for s in sp]
    inP = lambda i, x: (Pside[i] >> x) & 1
    moved = {i for i, s in enumerate(sp) if rv(s) != ((s >> p) & 1)}
    out["L1"] = moved == {i for i in range(len(sp)) if inP(i, a) and not inP(i, q) and not inP(i, d)} and \
        all(sep(sp[i], c, d) for i in range(len(sp)) if inP(i, a) and not inP(i, q)) and \
        all(inP(i, d) for i in range(len(sp)) if sep(sp[i], c, d) and not (inP(i, a) and not inP(i, q)))
    pred = {(min(i, j), max(i, j)) for i in moved for j in range(len(sp)) if j not in moved and (Pside[j] & ~Pside[i]) == 0}
    out["L2"] = pred == {(min(i, j), max(i, j)) for i, j in new}
    # K1: every gained uncrossed unmoved split gains exactly the moved splits
    nb = {}
    for i, j in new:
        nb.setdefault(i, set()).add(j)
        nb.setdefault(j, set()).add(i)
    out["K1"] = all(nb[u] == moved for u in gained if u not in moved) if moved else True
    out["gained"] = len(gained)
    out["F1_premise"] = bool(gained)                                   # the fill gives an uncrossed split a crossing
    out["T1"] = not (moved - active)
    mc = moved & active
    out["T2"] = orders is not None and mc in orders
    out["alpha"] = out["sign"] and out["T1"] and out["T2"] and bool(gained)
    out["beta"] = (not out["sign"]) and not gained and any(i in active and j in active for i, j in new)
    mid_all = all(sep(sp[i], p, q) for i in active)
    pd = {i for i in active if sep(sp[i], p, d)}
    out["pattern"] = mid_all and out["near_none"] and bool(pd) and pd != active
    out["mid_all"] = mid_all
    out["orders"] = tuple(sorted(len(o) for o in orders)) if orders else None
    out["marked"] = frozenset((trace(s, (q, a, c, d), p), i in active) for i, s in enumerate(sp))
    return out


def random_bracketing(m, rng):
    return CL.random_bracketing(m, rng)


def run(knots0, n0, nmax, seed_value, ablate_steps=0, ablate_nmax=0, closure=True):
    """A SEEDK run; after the switch, every crossing-making extension with SEED's verdict and the readings of each knot set.
    With ablate_steps > 0, also the first ablate_steps bases after the switch (n <= ablate_nmax) with fills on any pairs."""
    rng = random.Random(seed_value)
    S, G, knots, n = M.base(n0, knots0), M.pairs_of(knots0), list(knots0), n0
    rows, abl = [], []
    copies = 0
    fill_r = set()
    after_switch = 0
    while n < nmax:
        b = K.betti(n, knots)
        ops, kind = K.seedk_options(S, n, G, b["b2"])
        if not ops:
            break
        if b["b2"] > 0:
            after_switch += 1
            acc = {x[:2] for x in ops} if kind == "fill" else set()
            sp, Gc, active, orders = base_view(S, n)
            byext = {}
            for a0, a1, ks in L.moves(S, n, G):
                if P.pc(a0) + P.pc(a1) == len(S):
                    byext.setdefault((a0, a1), []).append(ks)
            for (a0, a1), cert in byext.items():
                new = P.new_crossings(S, n, a1)[0]
                if not new:
                    continue
                gained = sorted({v for e in new for v in e if v not in active})
                mine, _ = seed_verdict(sp, Gc, active, new)
                sets = []
                for ks in cert:
                    A = analyse(S, n, a1, ks, sp, Gc, active, orders, new, gained)
                    if A is None:
                        sets.append(None)
                        continue
                    f = shape(ks, n)
                    A["p_is_earlier_r"] = f["p"] in fill_r if f["p"] is not None else None
                    if closure:
                        A["closure"] = KL.wl(KL.picture_closure(S, n, ks))[:12]
                    sets.append(A)
                rows.append({"n": n, "seed": (a0, a1) in acc, "mine": mine, "sets": sets, "copies_before": copies,
                             "orders": tuple(sorted(len(o) for o in orders)) if orders else None, "splits": len(sp),
                             "active": len(active)})
            if ablate_steps and after_switch <= ablate_steps and n <= ablate_nmax:
                abl.extend(ablation(S, n, G, sp, Gc, active, orders))
        a0, a1, ks = rng.choice(ops)
        if kind == "fill" and b["b2"] > 0 and P.new_crossings(S, n, a1)[0]:
            copies += 1
        if kind == "fill":
            fill_r.add(n)
        S, G, knots, n = M.apply(S, n, a0, a1), G | M.pairs_of(ks), knots + list(ks), n + 1
    return rows, abl


def ablation(S, n, G, sp, Gc, active, orders):
    """Fills with knots on any pairs: for each crossing-making shaped knot set, which of its three pairs share a knot already, and
    its readings, with SEED's verdict computed from the clauses."""
    allp = {(u, v) for u, v in itertools.combinations(range(n), 2)}
    byext = {}
    for a0, a1, ks in L.moves(S, n, allp):
        if P.pc(a0) + P.pc(a1) == len(S):
            byext.setdefault((a0, a1), []).append(ks)
    out = []
    co = lambda x, y: (min(x, y), max(x, y)) in G
    for (a0, a1), cert in byext.items():
        new = P.new_crossings(S, n, a1)[0]
        if not new:
            continue
        gained = sorted({v for e in new for v in e if v not in active})
        seed, _ = seed_verdict(sp, Gc, active, new)
        for ks in cert:
            A = analyse(S, n, a1, ks, sp, Gc, active, orders, new, gained)
            if A is None or A.get("L1") is None:
                continue
            f = shape(ks, n)
            pat = (co(f["p"], f["q"]), co(f["a"], f["p"]), co(f["c"], f["d"]))
            out.append({"n": n, "seed": seed, "pattern_coknotted": pat, "sign": A["sign"], "F1_premise": A["F1_premise"],
                        "T1": A["T1"], "T2": A["T2"], "alpha": A["alpha"], "beta": A["beta"]})
    return out
