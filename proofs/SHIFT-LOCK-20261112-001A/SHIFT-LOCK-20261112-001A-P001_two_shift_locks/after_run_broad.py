#!/usr/bin/env python3
"""After the run (descriptive; not frozen): the cells of SHIFT-LOCK-20261112-001A where H0 failed, i.e. a mixed repeat unlocks although
no non-constant state is invariant, up to the shifts and flip of the harmony, along a short step.

    .venv/bin/python3 -B after_run_broad.py [--write]
For each such cell: (1) the found state is checked by direct evaluation of not-all-equal on its bits, with no use of R, and checked to
be invariant along no step at all, up to the shifts and flip; (2) the automorphisms of (W, R), every permutation of the harmony's states
keeping R, are found, and the cell is re-asked with them in place of the shifts and flip (a non-constant state invariant along a short
step up to some automorphism); (3) the copies tied to copy 0."""
import importlib.util
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
T0 = time.time()


def nae_check(h, n, m, words):
    """the state's words (ints, bit i = place i) satisfy every copy's own kinds and every mixed knot, by direct evaluation"""
    P = h["P"]
    bit = lambda w, i: (w >> (i % P)) & 1
    kinds = [(a, b) for (_, a, b) in h["kinds"]]
    cell = lambda r, c: (r % n) * m + (c % m)
    for x in range(n * m):
        w = words[x]
        for (a, b) in kinds:
            for i in range(P):
                if bit(w, i) == bit(w, i + a) == bit(w, i + b):
                    return False
    for r in range(n):
        for c in range(m):
            x, y, z = words[cell(r, c)], words[cell(r, c + 1)], words[cell(r + 1, c)]
            for (a, b) in kinds:
                for i in range(P):
                    if bit(x, i) == bit(y, i + a) == bit(z, i + b):
                        return False
    return len(set(words)) > 1


def automorphisms(S, limit=2000, max_states=20):
    """permutations of the states keeping R, by backtracking with degree refinement (all of them up to limit); None past max_states"""
    W, Rs = S["W"], S["Rset"]
    nW = len(W)
    if nW > max_states:
        return None
    sig = []
    for u in range(nW):
        sig.append((sum(1 for t in Rs if t[0] == u), sum(1 for t in Rs if t[1] == u), sum(1 for t in Rs if t[2] == u),
                    (u, u, u) in Rs))
    by = {}
    for t in Rs:
        for k in range(3):
            by.setdefault((k, t[k]), []).append(t)
    out = []

    def ok(mp):
        for u, pu in mp.items():
            for t in by.get((0, u), []):
                if all(x in mp for x in t) and (mp[t[0]], mp[t[1]], mp[t[2]]) not in Rs:
                    return False
        return True

    def rec(mp, used):
        if len(out) >= limit:
            return
        if len(mp) == nW:
            out.append(tuple(mp[u] for u in range(nW)))
            return
        u = len(mp)
        for v in range(nW):
            if v in used or sig[v] != sig[u]:
                continue
            mp[u] = v
            if ok(mp):
                used.add(v)
                rec(mp, used)
                used.discard(v)
            del mp[u]
    rec({}, set())
    return out


def short_under(S, L, n, m, perms):
    """a non-constant state with X(x + v) = pi(X(x)) at every copy, for a short step v and a permutation pi from perms; None if none"""
    from pysat.solvers import Solver
    Ppat = L.two_shift_pattern(n, m)
    cl, nv, var = L.E.build(Ppat, S["h"], "one order")
    extra, nxt = L.nonconstant_clauses(S, var, Ppat[0], nv + 1)
    P = S["P"]
    W = S["W"]
    cellf = L.cell(n, m)
    with Solver(name="cadical153", bootstrap_with=cl + extra) as s:
        for step in L.short_steps(n, m):
            for pi in perms:
                sel = nxt
                nxt += 1
                for r in range(n):
                    for c in range(m):
                        x, y = cellf(r, c), cellf(r + step[0], c + step[1])
                        for u in range(len(W)):
                            notu = [-var(x, i) if (W[u] >> i) & 1 else var(x, i) for i in range(P)]
                            tw = W[pi[u]]
                            for i in range(P):
                                s.add_clause([-sel] + notu + [var(y, i) if (tw >> i) & 1 else -var(y, i)])
                if s.solve(assumptions=[sel]):
                    return L.decode(S, s.get_model(), var, Ppat[0])
                s.add_clause([-sel])
    return None


def job(args):
    hname, cells = args
    import shift_lib as L
    hs = L.harmonies()
    h = [x for x in hs if L.name(x) == hname][0]
    S = L.setup(h)
    t = time.time()
    auts = automorphisms(S)
    Gperms = {g for (_, g) in S["G"]}
    extra = None if auts is None else [p for p in auts if p not in Gperms]
    out = {"harmony": hname, "states": len(S["W"]), "automorphisms of (W, R)": None if auts is None else len(auts),
           "of them not shifts and flips": None if extra is None else len(extra), "cells": []}
    for (n, m, X) in cells:
        words = [S["W"][u] for u in X]
        row = {"n": n, "m": m, "state verified by direct not-all-equal": nae_check(h, n, m, words),
               "invariant along some step up to shifts and flips": L.shortest_invariance(S, X, n, m) is not None}
        row["short state up to an automorphism outside the shifts and flips"] = "not computed" if extra is None else \
            (False if not extra else short_under(S, L, n, m, extra) is not None)
        row["copies tied to copy 0"] = tied_count(S, L, n, m, X)
        row["copies"] = n * m
        out["cells"].append(row)
    out["seconds"] = round(time.time() - t, 1)
    (HERE / "partial" / ("broad_%s.json" % hname.replace(" + ", "+")[:60])).write_text(json.dumps(out) + "\n")
    return out


def tied_count(S, L, n, m, X):
    """copies equal to copy 0 in every state, pruned by found states (starting from the given one)"""
    from pysat.solvers import Solver
    Ppat = L.two_shift_pattern(n, m)
    cl, nv, var = L.E.build(Ppat, S["h"], "one order")
    P = S["P"]
    cand = {c for c in range(1, n * m) if X[c] == X[0]}
    tied = 1
    with Solver(name="cadical153", bootstrap_with=cl) as s:
        nxt = nv + 1
        while cand:
            d = min(cand)
            sel, aux = nxt, []
            nxt += 1
            for p in range(P):
                y = nxt
                nxt += 1
                a, b = var(0, p), var(d, p)
                s.add_clause([-y, a, b])
                s.add_clause([-y, -a, -b])
                aux.append(y)
            s.add_clause([-sel] + aux)
            if s.solve(assumptions=[sel]):
                Y = L.decode(S, s.get_model(), var, n * m)
                cand = {c for c in cand if Y[c] == Y[0]}
            else:
                tied += 1
                cand.discard(d)
            s.add_clause([-sel])
    return tied


def main():
    two = json.loads((HERE / "result_two.json").read_text())["checks"]["result"]["rows"]
    work = {}
    for r in two:
        for x in r["rows"]:
            if x["unlocks"] and x["short"] is False:
                work.setdefault(r["harmony"], []).append((x["n"], x["m"], x["broad state"]))
    (HERE / "partial").mkdir(exist_ok=True)
    with Pool(11) as pool:
        rows = pool.map(job, sorted(work.items(), key=lambda kv: -len(kv[1])), chunksize=1)
    res = {"rows": rows, "seconds": round(time.time() - T0, 1)}
    print(json.dumps([{k: v for k, v in r.items() if k != "cells"} | {
        "verified": sum(c["state verified by direct not-all-equal"] for c in r["cells"]),
        "with any step": sum(c["invariant along some step up to shifts and flips"] for c in r["cells"]),
        "short under other automorphisms": sum(1 for c in r["cells"] if c["short state up to an automorphism outside the shifts and flips"]),
        "ties": sorted({(c["copies tied to copy 0"], c["copies"]) for c in r["cells"]}),
        "cells": len(r["cells"])} for r in rows], indent=0))
    if "--write" in sys.argv:
        (HERE / "result_after_run_broad.json").write_text(json.dumps(res, indent=1) + "\n")


if __name__ == "__main__":
    main()
