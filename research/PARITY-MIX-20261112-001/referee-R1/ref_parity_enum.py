#!/usr/bin/env python3
"""Referee PARITY-MIX-R1, the dense-parity classes: for the classes ref_parity_fast.py did not finish (dense parity knots, slow for
the one-hot two-copy encoding), the same measures with two copies of the lighter encoding compared up to flips bit by bit, by
CaDiCaL: flip-frozen and fixed by count 0 for the whole, B2 (own kinds and parity knots) and BN (own kinds and stitches); B1 as in
ref_parity.py. class_tuples (enumeration up to flips) and read are kept for spot checks against fixing_light.

    python3 -B ref_parity_enum.py <harmony name>      (appends to result_p4_rest.jsonl)"""
import json
import sys
import time
from pathlib import Path

from pysat.solvers import Solver

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ref_parity as RP  # noqa: E402
import ref_parity_fast as F  # noqa: E402

CAP = 200000


def light(st, n, K, use_nae=True):
    """the lighter encoding; with use_nae False, B2: each copy's own kinds and the parity knots only"""
    cl = F.light_cnf(st, n, K)
    if use_nae:
        return cl
    own = len(st["kinds"]) * st["P"] * 2 * n * n                      # each copy's own kinds come first
    return cl[:own] + [c for c in cl[own:] if len(c) == 4]          # parity clauses have four literals, stitches three


def class_tuples(st, n, cl):
    """every class tuple of the states, blocking each tuple up to flips (some copy differs from its word and from its flip)"""
    P, full = st["P"], st["full"]
    var = lambda x, i: x * P + i + 1
    nxt = max(abs(l) for c in cl for l in c) + 1
    out = set()
    with Solver(name="cadical153", bootstrap_with=cl) as s:
        while s.solve():
            m = s.get_model()
            words = [sum(1 << i for i in range(P) if m[var(x, i) - 1] > 0) for x in range(n * n)]
            out.add(tuple(min(w, w ^ full) for w in words))
            if len(out) >= CAP:
                return out, True
            block = []
            for x, w in enumerate(words):
                d, e, g = nxt, nxt + 1, nxt + 2
                nxt += 3
                s.add_clause([-d] + [(-var(x, i) if (w >> i) & 1 else var(x, i)) for i in range(P)])
                s.add_clause([-e] + [(var(x, i) if (w >> i) & 1 else -var(x, i)) for i in range(P)])
                s.add_clause([-g, d])
                s.add_clause([-g, e])
                block.append(g)
            s.add_clause(block)
    return out, False


def light_variant(st, n, K, which):
    """'whole', 'B2' (own kinds and parity knots) or 'BN' (own kinds and stitches)"""
    cl = F.light_cnf(st, n, K)
    if which == "whole":
        return cl
    own = len(st["kinds"]) * st["P"] * 2 * n * n                      # each copy's own kinds come first
    keep = 4 if which == "B2" else 3                                  # parity clauses have four literals, stitches three
    return cl[:own] + [c for c in cl[own:] if len(c) == keep]


def fixing_light(st, n, cl, want_frozen=True):
    """two copies of the lighter encoding: (frozen[r], fixed[r]) up to flips, by CaDiCaL"""
    P = st["P"]
    off = max(abs(l) for c in cl for l in c)
    a = lambda x, i: x * P + i + 1
    b = lambda x, i: a(x, i) + off
    both = cl + [[l + off if l > 0 else l - off for l in c] for c in cl]
    nxt = 2 * off + 1
    a0 = nxt
    nxt += 1
    for c in range(n):
        f = nxt
        nxt += 1
        for i in range(P):
            p, q = a(c, i), b(c, i)
            both += [[-a0, f, p, -q], [-a0, f, -p, q], [-a0, -f, p, q], [-a0, -f, -p, -q]]
    D = {}
    for r in range(1, n):
        D[r] = nxt
        nxt += 1
        gs = []
        for c in range(n):
            x = r * n + c
            g = nxt
            nxt += 1
            gs.append(g)
            ds, es = [], []
            for i in range(P):
                p, q = a(x, i), b(x, i)
                d, e = nxt, nxt + 1
                nxt += 2
                both += [[-d, p, q], [-d, -p, -q], [-e, p, -q], [-e, -p, q]]
                ds.append(d)
                es.append(e)
            both += [[-g] + ds, [-g] + es]
        both.append([-D[r]] + gs)
    frozen, fixed = [], []
    with Solver(name="cadical153", bootstrap_with=both) as s:
        for r in range(1, n):
            fr = (not s.solve(assumptions=[D[r]])) if want_frozen else None
            frozen.append(fr)
            fixed.append(bool(fr) or not s.solve(assumptions=[a0, D[r]]))
    return frozen, fixed


def read(ts, n):
    rows0 = lambda t: t[:n]
    frozen, fixed = [], []
    for r in range(1, n):
        cnt = lambda t: t[r * n:(r + 1) * n]
        frozen.append(len({cnt(t) for t in ts}) == 1)
        by0 = {}
        for t in ts:
            by0.setdefault(rows0(t), set()).add(cnt(t))
        fixed.append(all(len(v) == 1 for v in by0.values()))
    return frozen, fixed


def analyse_light(st, n, K, func, alive=None):
    """ref_parity.analyse's measures with the lighter two-copy check"""
    if alive is None:
        with Solver(name="cadical153", bootstrap_with=F.light_cnf(st, n, K)) as sv:
            alive = sv.solve()
    row = {"cells": sorted(K), "k": len(K), "state": alive}
    if alive:
        frozen, fixed = fixing_light(st, n, light_variant(st, n, K, "whole"))
        reach = RP.propagation(n, n, K, func)
        fbu = [r for r in range(n - 1) if fixed[r] and not frozen[r] and not reach[r]]
        row.update({"flip-frozen": sum(frozen), "fixed": sum(fixed), "reached": sum(reach), "fixed but unreached": len(fbu),
                    "full fixing": all(fixed) and not all(frozen)})
        if fbu:
            b1 = RP.gf2_fixed(n, n, K)
            fx2 = fixing_light(st, n, light_variant(st, n, K, "B2"), want_frozen=False)[1] if any(not b1[r] for r in fbu) else b1
            fxn = fixing_light(st, n, light_variant(st, n, K, "BN"), want_frozen=False)[1] \
                if any(not b1[r] and not fx2[r] for r in fbu) else fx2
            row["sources"] = ["B1 parity algebra" if b1[r] else "B2 parity and states" if fx2[r] else
                              "BN stitches alone" if fxn[r] else "only the whole" for r in fbu]
    return row


def main():
    name = sys.argv[1]
    n = 4
    hs = {RP.setup(h)["name"]: h for h in RP.hs()}
    st = RP.setup(hs[name])
    func = RP.census(st)["functional slots"]
    done = set()
    for fn in ("result_p4_fast.jsonl", "result_p4_rest.jsonl"):
        p = HERE / fn
        if p.exists():
            for line in p.read_text().splitlines():
                d = json.loads(line)
                if d["harmony"] == name and d.get("kinds", st["kinds"]) == st["kinds"]:
                    done.add(frozenset(d["rows"][0]["cells"]))
    t0 = time.time()
    for orb in RP.classes(n, n):
        if any(frozenset(K) in done for K in orb):
            continue
        rows = []
        for K in orb:
            with Solver(name="cadical153", bootstrap_with=F.light_cnf(st, n, K)) as sv:
                alive = sv.solve()
            row = analyse_light(st, n, K, func, alive)
            rows.append(row)
        with open(HERE / "result_p4_rest.jsonl", "a") as fh:
            fh.write(json.dumps({"harmony": name, "n": n, "rows": rows}) + "\n")
        print(len(orb[0]), [r["state"] for r in rows][:4], round(time.time() - t0), "s", flush=True)
    print("done", round(time.time() - t0, 1), "s")


if __name__ == "__main__":
    main()
