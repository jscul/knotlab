#!/usr/bin/env python3
"""Checks for SUBST-NEST-20261112-001A (research/SUBST-NEST-20261112-001/preregistration.md).

    .venv/bin/python3 -B check.py --part blocks|motifs|summary [--write]
blocks (arm D): every living connected block of 3 to 5 distinctions, and of 6 with up to 5 knots (87, one per isomorphism class),
with each canonical binding set: the template, the star places, and on chains of 4, 8 and 16 knots and the drawn three-copy nestings
of levels 1 to 3 (one substitution), and on chains of 4 and 8 knots and nestings of levels 1 and 2 (two substitutions): lives, and
for a root in every column of the chain's first distinction, its tie class, the ties outside the root's own copy, the farthest tie
and the farthest distinction. motifs (arm K): the two motifs, levels 0 to 4 (gasket to 5): the corner relation and the corner's
tie class, share, farthest tie, farthest distinction. summary: the frozen items. The independent referee is the background referee
thread's (referee pending)."""
import hashlib
import json
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
T0 = time.time()
DEPS = [str((HERE / f).relative_to(ROOT)) for f in ("subst_lib.py", "check.py")] + ["research/SUBST-NEST-20261112-001/preregistration.md"]
BLOCKS = None


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def tests():
    import subst_lib as S
    one = [("chain 4", S.chain(4)), ("chain 8", S.chain(8)), ("chain 16", S.chain(16)),
           ("nesting 1", S.gasket(1)), ("nesting 2", S.gasket(2)), ("nesting 3", S.gasket(3))]
    two = [("chain 4", S.chain(4)), ("chain 8", S.chain(8)), ("nesting 1", S.gasket(1)), ("nesting 2", S.gasket(2))]
    return [(1, n, P) for n, P in one] + [(2, n, P) for n, P in two]


def measure(P, B, T, k):
    import subst_lib as S
    Q, addr = S.iterate(P, B, T, k)
    inv = {a: i for i, a in addr.items()}
    m = B[0]
    out = {"distinctions": Q[0], "knots": len(Q[1]), "roots": []}
    for p in range(m):
        root = inv[(0,) + (p,) * k]
        tied = S.tie_class(Q, root)
        if tied is None:
            out["lives"] = False
            return out
        out["lives"] = True
        d = S.distances(Q, root)
        cross = [v for v in tied if addr[v][0] != 0]
        out["roots"].append({"column": p, "tied": len(tied), "share": round(len(tied) / Q[0], 6), "tied outside the root's copy": len(cross),
                             "farthest tie": max(d[v] for v in tied), "farthest distinction": max(d.values())})
    return out


def block_job(i):
    import subst_lib as S
    m, Bk = BLOCKS[i]
    B = (m, Bk)
    rows = []
    for tname, T in S.binding_sets(m, Bk).items():
        t = time.time()
        sols, K = S.template(B, T)
        row = {"binding": tname, "block states": len(sols), "template knots": len(K),
               "rigid (only constant template knots)": all(a == b == c for (a, b, c) in K),
               "star places": S.star_colouring(B) if tname == "the block's knots" else None, "tests": []}
        for k, name, P in tests():
            r = measure(P, B, T, k)
            r.update({"substitutions": k, "pattern": name})
            rows_ = r
            row["tests"].append(rows_)
        row["seconds"] = round(time.time() - t, 1)
        rows.append(row)
    return {"block": [m, Bk], "bindings": rows}


def motif_job(name):
    import subst_lib as S
    M = S.MOTIFS[name]
    out = {"motif": name, "corner relation after one level": S.motif_flow(M), "levels": []}
    top = 6 if "gasket" in name else 5
    for L in range(0, top):
        Q = S.motif_level(M, L)
        tied = S.tie_class(Q, 0)
        if tied is None:
            out["levels"].append({"level": L, "lives": False})
            continue
        d = S.distances(Q, 0)
        from pysat.solvers import Solver
        corners = set()
        with Solver(name="cadical153", bootstrap_with=S.nae_clauses(Q[1])) as s:
            while s.solve():
                mm = s.get_model()
                c = tuple(int(mm[x] > 0) for x in (0, 1, 2))
                corners.add(c)
                s.add_clause([-(x + 1) if mm[x] > 0 else (x + 1) for x in (0, 1, 2)])
        out["levels"].append({"level": L, "distinctions": Q[0], "knots": len(Q[1]), "lives": True, "corner relation": sorted(corners),
                              "tied to corner 0": len(tied), "share": round(len(tied) / Q[0], 6),
                              "farthest tie": max(d[v] for v in tied), "farthest distinction": max(d.values())})
    return out


def init(bl):
    global BLOCKS
    BLOCKS = bl


def run_part(part):
    import subst_lib as S
    if part == "blocks":
        bl = S.blocks()
        with Pool(12, initializer=init, initargs=(bl,)) as pool:
            return {"blocks": len(bl), "rows": pool.map(block_job, range(len(bl)), chunksize=1)}
    if part == "motifs":
        return {"rows": [motif_job(n) for n in S.MOTIFS]}


def summary():
    bl = json.loads((HERE / "result_blocks.json").read_text())["checks"]["result"]["rows"]
    mo = json.loads((HERE / "result_motifs.json").read_text())["checks"]["result"]["rows"]

    def cross(t):
        return t["lives"] and any(r["tied outside the root's copy"] for r in t["roots"])

    def ratio(t):
        return max((r["farthest tie"] / r["farthest distinction"]) for r in t["roots"]) if t["lives"] else None
    cells = [(b["block"], x) for b in bl for x in b["bindings"]]
    K4 = [x for blk, x in cells if blk[0] == 4 and len(blk[1]) == 4 and x["binding"] == "the block's knots"][0]
    one = [x for blk, x in cells if blk[0] == 3 and x["binding"] == "the block's knots"][0]
    grows = [(blk, x["binding"]) for blk, x in cells if all(cross(t) and ratio(t) >= 0.5 for t in x["tests"] if t["substitutions"] == 1 and t["pattern"].startswith("chain"))]
    some_cross = [(blk, x["binding"]) for blk, x in cells if any(cross(t) for t in x["tests"])]
    deeper = [(blk, x["binding"]) for blk, x in cells
              if not any(cross(t) for t in x["tests"] if t["substitutions"] == 1) and any(cross(t) for t in x["tests"] if t["substitutions"] == 2)]
    star_all = [(blk, x) for blk, x in cells if x["binding"] == "the block's knots" and x["star places"] is not None and len(x["star places"]) == blk[0]]
    return {
        "cells (block, binding)": len(cells),
        "S1 diagonal: no tie outside the root's copy, for every block": not any(cross(t) for blk, x in cells if x["binding"] == "diagonal" for t in x["tests"]),
        "S2 blocks with a star at every place, bound by their knots: no tie outside the copy": all(not any(cross(t) for t in x["tests"]) for blk, x in star_all),
        "S2 such blocks": len(star_all),
        "S3 all four knots on four distinctions, bound by its knots: rigid template": K4["rigid (only constant template knots)"],
        "S3 its tests: lives, ties outside the copy, ratio, share": [[t["substitutions"], t["pattern"], t["lives"], cross(t), ratio(t), max(r["share"] for r in t["roots"])] for t in K4["tests"]],
        "S3b one knot, bound by its knots: no tie outside the copy": not any(cross(t) for t in one["tests"]),
        "S4 rigid cells": [(blk, x["binding"]) for blk, x in cells if x["rigid (only constant template knots)"]],
        "S5 cells with ties outside the copy but not rigid (intermediate)": [(blk, x["binding"]) for blk, x in cells
                                                                             if any(cross(t) for t in x["tests"]) and not x["rigid (only constant template knots)"]],
        "S6 cells whose influence grows with the chain (ratio >= 1/2 on chains of 4, 8, 16)": grows,
        "cells with any tie outside the root's copy": len(some_cross),
        "cells where such ties appear only after two substitutions": deeper,
        "cells that end on some test": [(blk, x["binding"]) for blk, x in cells if any(not t["lives"] for t in x["tests"])],
        "K1 gasket motif: free after one level, no ties at levels 1 to 5": [m for m in mo if "gasket" in m["motif"]][0]["corner relation after one level"] == [list(c) for c in __import__("itertools").product((0, 1), repeat=3)]
            and all(L["tied to corner 0"] == 1 for m in mo if "gasket" in m["motif"] for L in m["levels"][1:]),
        "K2 Fano motif: corners equal; tied to corner 0 at levels 0 to 4, share, farthest tie, farthest distinction":
            [[L["level"], L["tied to corner 0"], L["share"], L["farthest tie"], L["farthest distinction"]] for m in mo if "Fano" in m["motif"] for L in m["levels"]],
    }


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    part = sys.argv[sys.argv.index("--part") + 1]
    write = "--write" in sys.argv
    res = summary() if part == "summary" else run_part(part)
    res = {"dependencies": {p: sha(p) for p in DEPS}, "result": res, "seconds": round(time.time() - T0, 1)}
    path = HERE / ("result_%s.json" % part if part != "summary" else "result.json")
    if write:
        path.write_text(json.dumps({"status": "passed", "checks": res}, indent=1, default=str) + "\n")
        print("wrote", path, round(time.time() - T0, 1), "s")
    else:
        old = json.loads(path.read_text())["checks"]
        same = json.dumps(old["result"], sort_keys=True, default=str) == json.dumps(json.loads(json.dumps(res["result"], default=str)), sort_keys=True)
        print("result reproduced" if same else "result differs")
        sys.exit(0 if same else 1)


if __name__ == "__main__":
    main()
