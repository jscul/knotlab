"""COPY-CLASS-20261118-001B-E001: what SEED's copy step reads.

COPY-READ-20261118-001 found every absorbing fill (a crossing-making fill SEED accepts after its switch) in one closure class, with
about 55 refused fills for each absorbing one.  By MID-RULE-20261118-001A, E1, every new crossing joins a split separating one end
pair of the certificate to a split separating the other.  So SEED's two clauses can be read on those splits:
- clause (a): no new crossing between two splits that already crossed something;
- clause (b): every split that crossed nothing and gains crossings ends with exactly the crossers of a crossed split, the model.
The candidate local rule CR (the advisor's) looks for the model only among the splits separating the end pair that shares a
distinction with the middle knot's pair, and reads clause (a) only on the two end pairs' splits.  CRANY looks for the model among all
crossed splits (SEED's own clause (b)); both are compared with SEED's verdict on every crossing-making knot set.
"""
import itertools
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.append(os.path.join(ROOT, "experiments", "KEEP-READ-20261118-001B", "KEEP-READ-20261118-001B-E001_keep"))
import keeplib as KL  # noqa: E402

K, M, L, P = KL.K, KL.M, KL.L, KL.P
COPY_CLASS = "61f46d7f8948"            # COPY-READ-20261118-001's closure class of every absorbing fill


def separating(sp, u, v):
    return [i for i, s in enumerate(sp) if ((s >> u) & 1) != ((s >> v) & 1)]


def verdicts(S, n, ks, a1, sp, Gc):
    """For one crossing-making knot set: the local new crossings (between the two end pairs' splits), whether they equal all new
    crossings, and the verdicts of CR and CRANY with the reason for a refusal."""
    full = (1 << n) - 1
    idx = {x: i for i, x in enumerate(S)}
    val = lambda X: (a1 >> idx[X]) & 1
    ends = [k for k in ks if k[1] != n]
    mids = [k for k in ks if k[1] == n]
    pairs_end = [tuple(x for x in k if x != n) for k in ends]
    out = {"ends": len(ends), "middles": len(mids)}
    if len(ends) < 2:
        out.update({"cr": False, "crany": False, "reason": "fewer than two end knots", "local_equals_all": None})
        return out
    sep_sets = [set(separating(sp, *p)) for p in pairs_end]
    local = set()
    for i in set().union(*sep_sets):
        for j in set().union(*sep_sets):
            if i < j and not Gc.has_edge(i, j):
                a, b = sp[i], sp[j]
                for X in (a, full ^ a):
                    for Y in (b, full ^ b):
                        if X & Y == 0 and val(X) and val(Y):
                            local.add((i, j))
    allnew = set(P.new_crossings(S, n, a1)[0])
    out["local_equals_all"] = local == allnew
    active = {v for v in Gc if Gc.degree(v) > 0}
    if any(i in active and j in active for i, j in local):
        out.update({"cr": False, "crany": False, "reason": "(a) crossed splits come to cross"})
        return out
    newN = {}
    for i, j in local:
        newN.setdefault(i, set()).add(j)
        newN.setdefault(j, set()).add(i)
    gained = [u for u in newN if u not in active]
    after = {v: set(Gc[v]) | newN.get(v, set()) for v in Gc}
    # the model end pair: the end pair sharing a distinction with the middle knot's pair
    mid_pair = set(x for x in mids[0] if x != n) if mids else set()
    model_idx = [t for t, p in enumerate(pairs_end) if mid_pair & set(p)]
    models_local = set()
    for t in model_idx:
        models_local |= {m for m in sep_sets[t] if m in active}
    ok_local = all(any(after[m] == after[u] for m in models_local) for u in gained)
    ok_any = all(any(after[m] == after[u] for m in active) for u in gained)
    reason = None
    if not ok_any:
        sub = all(any(after[u] < after[m] for m in active) for u in gained)
        sup = all(any(after[u] > after[m] for m in active) for u in gained)
        reason = "(b) a strict subset of a model's crossers" if sub else ("(b) a strict superset" if sup else "(b) mixed")
    out.update({"cr": ok_local, "crany": ok_any, "reason": reason,
                "model_found_locally": bool(models_local), "gained": len(gained),
                "model_crossers": max((len(Gc[m]) for m in models_local), default=0), "splits": len(sp)})
    return out


def random_bracketing(m, rng):
    """A random bracketing of the line 0..m by recursive random split points (not uniform over bracketings; declared)."""
    out = []

    def rec(a, b):
        if b - a <= 1:
            return
        c = rng.randrange(a + 1, b)
        out.append((a, c, b))
        rec(a, c)
        rec(c, b)
    rec(0, m)
    return out


def run(knots0, n0, nmax, seed_value):
    """A SEEDK run; after the switch, every crossing-making knot set with SEED's verdict on its extension, its closure class, and
    CR's and CRANY's verdicts."""
    rng = random.Random(seed_value)
    S, G, knots, n = M.base(n0, knots0), M.pairs_of(knots0), list(knots0), n0
    rows = []
    while n < nmax:
        b = K.betti(n, knots)
        ops, kind = K.seedk_options(S, n, G, b["b2"])
        if not ops:
            break
        if b["b2"] > 0:
            acc = {x[:2] for x in ops} if kind == "fill" else set()
            sp, Gc = P.crossing_graph(S, n)
            mv = L.moves(S, n, G)
            memo = {}
            for a0, a1, ks in [x for x in mv if P.pc(x[0]) + P.pc(x[1]) == len(S)]:
                if (a0, a1) not in memo:
                    memo[(a0, a1)] = bool(P.new_crossings(S, n, a1)[0])
                if not memo[(a0, a1)]:
                    continue
                v = verdicts(S, n, ks, a1, sp, Gc)
                v.update({"n": n, "ext": [a0, a1], "seed": (a0, a1) in acc,
                          "copy_class": KL.wl(KL.picture_closure(S, n, ks))[:12] == COPY_CLASS})
                rows.append(v)
        a0, a1, ks = rng.choice(ops)
        S, G, knots, n = M.apply(S, n, a0, a1), G | M.pairs_of(ks), knots + list(ks), n + 1
    return rows
