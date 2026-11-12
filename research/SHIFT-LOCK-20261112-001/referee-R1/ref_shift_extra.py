#!/usr/bin/env python3
"""Referee SHIFT-LOCK-R1: three checks on the 78 cells (mixed knot; unlocks, but no non-constant state repeats along a short step).

1. Ties: in each cell, every distinction of copy (0, 0) tied to a distinction of another copy (the referee's tie relation, Glucose).
2. Longer steps: whether some non-constant state repeats along ANY step of the repeat (not only sup-norm at most 2), up to the
   harmony's shifts and flip.
3. Other symmetries: Aut(R), the permutations of the harmony's states that preserve the one-knot relation R, found as automorphisms of
   R's three two-member projections (networkx VF2, labelled edges) filtered on R itself; then, where Aut(R) is larger than
   <shift, flip>, whether some non-constant state repeats along a short step up to an extra automorphism.
Where Aut(R) has more than 200 elements the third check is not run (two harmonies). Writes result_extra.json."""
import itertools
import json
import sys
import time
from pathlib import Path

import networkx as nx
import numpy as np
from networkx.algorithms.isomorphism import DiGraphMatcher
from pysat.solvers import Glucose4

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "ENDLESS-BLOCK-20261112-001" / "referee-R1"))
import ref_shift as S  # noqa: E402
import ref_endless as E  # noqa: E402
sys.path.insert(0, str(HERE.parents[1] / "BASES-WITHIN-20261112-001" / "referee-R1"))
import ref_ties as T  # noqa: E402


def aut_R(h):
    W, ok = E.relation(h)
    n = len(W)
    G = nx.DiGraph()
    G.add_nodes_from(range(n))
    proj = [ok.any(axis=2), ok.any(axis=1), ok.any(axis=0)]      # (u, v), (u, w), (v, w)
    for u in range(n):
        for v in range(n):
            lab = tuple(bool(p[u, v]) for p in proj)
            if any(lab):
                G.add_edge(u, v, lab=lab)
    selfl = {u: tuple(bool(ok[u, u, u]) for _ in range(1)) for u in range(n)}
    nx.set_node_attributes(G, selfl, "self")
    gm = DiGraphMatcher(G, G, node_match=lambda a, b: a["self"] == b["self"], edge_match=lambda a, b: a["lab"] == b["lab"])
    auts = []
    trip = np.argwhere(ok)
    Rset = {tuple(t) for t in trip.tolist()}
    for iso in gm.isomorphisms_iter():
        pi = [iso[u] for u in range(n)]
        if all((pi[a], pi[b], pi[c]) in Rset for a, b, c in Rset):
            auts.append(tuple(pi))
        if len(auts) > 200:
            break
    return W, auts


def shift_flip_perms(h, W):
    P = h["P"]
    idx = {tuple(w): i for i, w in enumerate(W)}
    out = set()
    for a in range(P):
        for e in (0, 1):
            out.add(tuple(idx[tuple((w[(i + a) % P]) ^ e for i in range(P))] for w in W))
    return out


def invariant_under(h, n, m, W, step, pi, cl, var):
    """a non-constant state with X(x + step) = pi(X(x)): encoded with one indicator per copy and state"""
    P = h["P"]
    nW = len(W)
    base = n * m * P + 10 ** 6
    y = lambda c, s: base + c * nW + s + 1
    extra = []
    copies = [(r, c) for r in range(n) for c in range(m)]
    cid = {xc: k for k, xc in enumerate(copies)}
    for (r, c) in copies:
        k = cid[(r, c)]
        extra.append([y(k, s) for s in range(nW)])
        for s in range(nW):
            for i in range(P):
                lit = var(r, c, i) if W[s][i] else -var(r, c, i)
                extra.append([-y(k, s), lit])
        k2 = cid[((r + step[0]) % n, (c + step[1]) % m)]
        for s in range(nW):
            extra.append([-y(k, s), y(k2, pi[s])])
    with Glucose4(bootstrap_with=cl + extra) as so:
        return so.solve()


def cross_ties(cl, n, m, P, var, rounds=64, seed=3):
    """pairs (place i of copy (0, 0), a distinction of another copy) with one relation in every state"""
    import random
    rng = random.Random(seed)
    nv = n * m * P
    with Glucose4(bootstrap_with=cl) as so:
        assert so.solve()
        X = []
        for _ in range(rounds):
            so.set_phases([v if rng.random() < 0.5 else -v for v in range(1, nv + 1)])
            so.solve()
            md = so.get_model()
            X.append([1 if md[v - 1] > 0 else 0 for v in range(1, nv + 1)])
        X = np.array(X, dtype=np.uint8)
        found = []
        for i in range(P):
            d = var(0, 0, i) - 1
            for e in range(P, nv):
                x = X[:, d] ^ X[:, e]
                if np.all(x == x[0]):
                    r = int(x[0])
                    other = [-(d + 1), (e + 1) if r == 0 else -(e + 1)]   # x_d = 0 and x_e = 1 - r
                    if not so.solve(assumptions=other):
                        found.append([i, e, r])
        return found


def main():
    rows = [json.loads(l) for l in open(HERE / "result_mixed.jsonl")]
    cells = [r for r in rows if not r["locks"] and not r["short-step state"]]
    hs = S.hs()
    out = {"cells": [], "harmonies": {}}
    for hi in sorted({c["i"] for c in cells}):
        h = hs[hi]
        t0 = time.time()
        W, auts = aut_R(h)
        sf = shift_flip_perms(h, W)
        extra = [p for p in auts if p not in sf]
        out["harmonies"][str(hi)] = {"orbits": h["orbits"], "states": len(W), "|Aut(R)|": len(auts), "|<shift, flip>|": len(sf),
                                     "extra automorphisms": len(extra), "seconds": round(time.time() - t0, 1)}
        print(hi, h["orbits"][:2], len(W), len(auts), len(sf), round(time.time() - t0, 1), flush=True)
        for c in [c for c in cells if c["i"] == hi]:
            n, m = c["n"], c["m"]
            cl, var = S.base_cnf(h, n, m)
            rec = {"i": hi, "n": n, "m": m}
            # 2. any step at all, shifts and flip
            longer = None
            for a in range(n):
                for b in range(m):
                    if (a, b) == (0, 0):
                        continue
                    for sh in range(h["P"]):
                        for e in (0, 1):
                            ex = []
                            for r in range(n):
                                for cc in range(m):
                                    for i in range(h["P"]):
                                        x1, y1 = var(r + a, cc + b, i), var(r, cc, i + sh)
                                        ex += [[x1, y1], [-x1, -y1]] if e else [[-x1, y1], [x1, -y1]]
                            with Glucose4(bootstrap_with=cl + ex) as so:
                                if so.solve():
                                    longer = [[a, b], sh, e]
                                    break
                        if longer:
                            break
                    if longer:
                        break
                if longer:
                    break
            rec["a non-constant state along some step (any length)"] = longer
            # 3. short steps up to extra automorphisms
            hit = None if len(auts) <= 200 else "not checked: more than 200 automorphisms"
            for st in (S.steps(n, m) if len(auts) <= 200 else []):
                for pi in extra:
                    if invariant_under(h, n, m, W, st, pi, cl, var):
                        hit = [list(st), "extra automorphism"]
                        break
                if hit:
                    break
            rec["short step up to an extra automorphism"] = hit
            # 1. ties of copy 0 with other copies (the cell without the non-constant clause)
            rec["ties of copy (0, 0) with other copies"] = cross_ties(cl[:-1], n, m, h["P"], var)
            out["cells"].append(rec)
            print("  ", n, m, longer, hit, flush=True)
    (HERE / "result_extra.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
