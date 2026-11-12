#!/usr/bin/env python3
"""Referee TWIST-PIN-R1: twisted pins with the referee's own code (ref_subst.py of the SUBST-NEST referee folder, the referee's; no
import of twist_lib.py, subst_lib.py or check.py).

    python3 -B ref_twist.py      (writes result_twist.json)

1. The binding's form: with the block's knots in every order, three copies' states are allowed exactly when every knot of the block
   holds at most one place where they are not unanimous; brute force on all 87 blocks.
2. The blocks whose symmetries move a distinction they cannot spare, and the classes of their non-identity symmetries.
3. Cells: each such block and class h on a chain of 4 knots, on closed chains of 2, 3 and 6 knots and on two closed chains of 3
   sharing a distinction, with the twist placed (a) as frozen (knot 0's second member) and (b) on the cycle (knot 0's first member);
   and the one-shift rings of 6 and 7 with every knot's middle member twisted by an involution. Measured: lives, the whole tie
   relation, the root copy's ties inside it. Predicted: (i) the frozen quotient (states of B constant on the H-orbits of the
   distinctions B cannot spare); (ii) for one cycle of k knots, the referee's move-graph prediction: the root copy's states are the
   states t of B with t o h within k moves of t, a move changing a set of places that meets every knot of B at most once."""
import itertools
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "SUBST-NEST-20261112-001" / "referee-R1"))
import ref_subst as S  # noqa: E402


def automorphisms(m, K):
    Ks = {frozenset(e) for e in K}
    return [g for g in itertools.permutations(range(m)) if {frozenset(g[x] for x in e) for e in K} == Ks]


def comp(a, b):
    return tuple(a[b[x]] for x in range(len(b)))


def inv(a):
    out = [0] * len(a)
    for i, x in enumerate(a):
        out[x] = i
    return tuple(out)


def classes(G):
    seen, reps = set(), []
    for g in sorted(G):
        if g in seen:
            continue
        seen |= {comp(comp(h, g), inv(h)) for h in G}
        reps.append(g)
    return reps


def group(gens, m):
    G = {tuple(range(m))}
    fr = list(G)
    while fr:
        g = fr.pop()
        for h in gens:
            k = comp(h, g)
            if k not in G:
                G.add(k)
                fr.append(k)
    return G


def twisted(P, m, K, twist):
    """sigma(P), the block's knots in every order between copies; member at slot s of knot e reads distinction g(p) of its copy"""
    n, PK = P
    ident = tuple(range(m))
    T = sorted({q for e in K for q in itertools.permutations(e)})
    knots = [(v * m + a, v * m + b, v * m + c) for v in range(n) for a, b, c in K]
    for ei, (x, y, z) in enumerate(PK):
        gx, gy, gz = (twist.get((ei, s), ident) for s in range(3))
        knots += [(x * m + gx[p], y * m + gy[q], z * m + gz[r]) for p, q, r in T]
    return (n * m, knots)


def holonomy(P, m, twist, root=0):
    """the group generated at the root copy by the symmetries carried around closed walks (moving through knot e from slot i to
    slot j carries a distinction q of the first copy to g_j(g_i^-1(q)) of the second)"""
    n, PK = P
    ident = tuple(range(m))
    steps = []
    for ei, mem in enumerate(PK):
        gs = [twist.get((ei, s), ident) for s in range(3)]
        for i in range(3):
            for j in range(3):
                if i != j:
                    steps.append((mem[i], mem[j], comp(gs[j], inv(gs[i]))))
    tau = {root: ident}
    fr = [root]
    while fr:
        v = fr.pop()
        for a, b, T in steps:
            if a == v and b not in tau:
                tau[b] = comp(T, tau[v])
                fr.append(b)
    gens = {comp(inv(tau[b]), comp(T, tau[a])) for a, b, T in steps if a in tau and b in tau}
    gens.discard(ident)
    return group(gens, m)


def own_ties(sts, m):
    return {p: {q for q in range(m) if len({s[p] ^ s[q] for s in sts}) == 1} for p in range(m)}


def classify(H, N, ties, m):
    if all(g == tuple(range(m)) for g in H):
        return "balanced"
    return "N-twisted" if any(g[q] != q and g[q] not in ties[q] for g in H for q in N) else "N-balanced"


def relation_of(states_list, m):
    """pairs (p, q), p < q, tied in every state of the list, with the relation"""
    if not states_list:
        return None
    return {(p, q): states_list[0][p] ^ states_list[0][q] for p in range(m) for q in range(p + 1, m)
            if len({s[p] ^ s[q] for s in states_list}) == 1}


def moves_graph(sts, K, m):
    adj = {i: [] for i in range(len(sts))}
    for i, a in enumerate(sts):
        for j, b in enumerate(sts):
            D = {p for p in range(m) if a[p] != b[p]}
            if all(len(D & set(e)) <= 1 for e in K):
                adj[i].append(j)
    return adj


def dist(adj, i, j):
    d = {i: 0}
    fr = [i]
    while fr and j not in d:
        nx = []
        for u in fr:
            for w in adj[u]:
                if w not in d:
                    d[w] = d[u] + 1
                    nx.append(w)
        fr = nx
    return d.get(j)


def closed_chain(k):
    n = 2 * k
    return (n, [(2 * i, 2 * i + 1, (2 * i + 2) % n) for i in range(k)])


PATTERNS = {"chain 4": (S.chain(4), None), "cycle 2": ((4, [(0, 1, 2), (0, 1, 3)]), 2), "cycle 3": (closed_chain(3), 3),
            "cycle 6": (closed_chain(6), 6), "two cycles": ((11, [(0, 1, 2), (2, 3, 4), (4, 5, 0), (0, 6, 7), (7, 8, 9), (9, 10, 0)]), None)}


def measure(Q, m, root_copy=0):
    rel = S.tie_relation(*Q, seed=5)
    if rel is None:
        return {"lives": False}
    inside = {(u - root_copy * m, v - root_copy * m): r for (u, v), r in rel.items()
              if root_copy * m <= u < (root_copy + 1) * m and root_copy * m <= v < (root_copy + 1) * m}
    outside = sum(1 for (u, v) in rel if (u // m) != (v // m))
    return {"lives": True, "inside": inside, "pairs between copies": outside}


def main():
    t0 = time.time()
    bl = S.blocks()
    res = {"binding form holds on all blocks": None, "blocks": [], "cells": [], "rings": []}
    form_ok = True
    for m, K in bl:
        sts = S.states(m, K)
        T = sorted({q for e in K for q in itertools.permutations(e)})
        for a in sts:
            for b in sts:
                for c in sts:
                    ok = all(S.nae(a[x], b[y], c[z]) for x, y, z in T)
                    D = {p for p in range(m) if not (a[p] == b[p] == c[p])}
                    if ok != all(len(D & set(e)) <= 1 for e in K):
                        form_ok = False
    res["binding form holds on all blocks"] = form_ok
    for m, K in bl:
        K = [tuple(e) for e in K]
        sts = S.states(m, K)
        N = [p for p in range(m) if p not in set(S.spare(m, K))]
        G = automorphisms(m, K)
        if not any(g[q] != q for g in G for q in N):
            continue
        ties = own_ties(sts, m)
        adj = moves_graph(sts, K, m)
        idx = {s: i for i, s in enumerate(sts)}
        cl = [g for g in classes(G) if g != tuple(range(m))]
        res["blocks"].append({"block": [m, [list(e) for e in K]], "not spare": N, "symmetries": len(G), "classes": len(cl)})
        for h in cl:
            for pname, (P, k) in PATTERNS.items():
                for place in ("frozen", "on the cycle"):
                    if pname == "two cycles":
                        # one class per cycle; the census used pairs of classes: here the same class on both cycles
                        tw = {(0, 1): h, (3, 1): h} if place == "frozen" else {(0, 0): h, (3, 0): h}
                    else:
                        tw = {(0, 1): h} if place == "frozen" else {(0, 0): h}
                    if pname == "cycle 2" and place == "on the cycle":
                        tw = {(1, 0): h}
                    H = holonomy(P, m, tw)
                    kind = classify(H, N, ties, m)
                    Q = twisted(P, m, K, tw)
                    meas = measure(Q, m)
                    qs = [s for s in sts if all(s[q] == s[g[q]] for g in H for q in N)]
                    pred_q = relation_of(qs, m)
                    row = {"block": [m, [list(e) for e in K]], "h": list(h), "pattern": pname, "placement": place, "class": kind,
                           "holonomy order": len(H), "lives": meas["lives"],
                           "quotient: some state constant on N-orbits": bool(qs),
                           "quotient: some state fixed by H": any(all(s[g[q]] == s[q] for g in H for q in range(m)) for s in sts)}
                    if meas["lives"]:
                        mi = {f"{p},{q}": r for (p, q), r in meas["inside"].items()}
                        row["ties inside the root copy"] = mi
                        row["new ties inside (not the block's own)"] = sorted(k_ for k_ in mi if int(k_.split(",")[1]) not in ties[int(k_.split(",")[0])])
                        row["quotient = measured"] = pred_q == meas["inside"]
                    if k is not None and len(H) > 1:
                        # one cycle of k knots with holonomy generated by one element hh (the gauge puts it on one knot)
                        hh = [g for g in H if g != tuple(range(m))]
                        gen = None
                        for g in hh:
                            if group({g}, m) == H:
                                gen = g
                                break
                        if gen is not None:
                            reach = [s for s in sts if tuple(s[gen[x]] for x in range(m)) in idx and
                                     (dist(adj, idx[s], idx[tuple(s[gen[x]] for x in range(m))]) or 0) <= k and
                                     dist(adj, idx[s], idx[tuple(s[gen[x]] for x in range(m))]) is not None]
                            row["move prediction: lives"] = bool(reach)
                            row["move prediction = lives"] = bool(reach) == meas["lives"]
                            if meas["lives"] and place == "on the cycle":    # the root copy carries the twist: it is the walk's end
                                row["move prediction of the root copy's ties = measured"] = relation_of(reach, m) == meas["inside"]
                    res["cells"].append(row)
        # rings with every knot's middle member twisted by an involution
        for h in cl:
            if comp(h, h) != tuple(range(m)):
                continue
            for n in (6, 7):
                P = (n, [(i, (i + 1) % n, (i + 2) % n) for i in range(n)])
                tw = {(i, 1): h for i in range(n)}
                H = holonomy(P, m, tw)
                meas = measure(twisted(P, m, K, tw), m)
                res["rings"].append({"block": [m, [list(e) for e in K]], "h": list(h), "ring": n, "class": classify(H, N, ties, m),
                                     "holonomy order": len(H), "lives": meas["lives"]})
    res["seconds"] = round(time.time() - t0, 1)
    (HERE / "result_twist.json").write_text(json.dumps(res, indent=1) + "\n")
    print("wrote result_twist.json", res["seconds"], "s")


if __name__ == "__main__":
    main()
