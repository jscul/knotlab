#!/usr/bin/env python3
"""Checks for TWIST-PIN-20261112-001A (research/TWIST-PIN-20261112-001/preregistration.md).

    .venv/bin/python3 -B check.py --part relation|twists|summary [--write]
relation: the advisor's form of the untwisted binding (three copies' states are allowed exactly when every knot of the block holds at
most one place where they are not unanimous) on all 87 census blocks. twists: the 18 census blocks with a symmetry moving a
distinction they cannot spare, every non-identity class of their symmetries, on a forest (a chain of 4 knots), one cycle of 2, 3 and 6
knots, two cycles of 3 knots through one distinction (with every pair of classes, at most 6 per block), and the one-shift ring of 6
and of 7 distinctions with the middle member of every knot twisted: lives, the root copy's ties, the holonomy group and its class,
the quotient prediction, and for one cycle the advisor's state-graph distance. summary: the frozen items. Referee: the background
referee thread (referee pending)."""
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
DEPS = [str((HERE / f).relative_to(ROOT)) for f in ("twist_lib.py", "check.py")] + \
       ["proofs/SUBST-NEST-20261112-001A/SUBST-NEST-20261112-001A-P001_block_substitution/subst_lib.py",
        "research/TWIST-PIN-20261112-001/preregistration.md"]
BLOCKS = None


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def eligible(bl):
    import twist_lib as W
    out = []
    for m, E in bl:
        B = (m, [tuple(e) for e in E])
        G = W.automorphisms(B)
        N = [p for p in range(m) if p not in set(W.S.star_colouring(B))]
        reps = [g for g in W.conjugacy_classes(G) if g != tuple(range(m))]
        if any(g[q] != q for g in reps for q in N):
            out.append(B)
    return out


def own_ties(B):
    import twist_lib as W
    m, E = B
    sts = W.S.solutions(m, E)
    return {p: {q for q in range(m) if len({s[p] ^ s[q] for s in sts}) == 1} for p in range(m)}


def measure(B, P, twist, cycle_len=None):
    import twist_lib as W
    m = B[0]
    N = [p for p in range(m) if p not in set(W.S.star_colouring(B))]
    Q, idx = W.twisted(P, B, twist)
    Q0, idx0 = W.twisted(P, B, {})
    H = W.holonomy_group(P, B, twist)
    cls = W.classify(B, H, N, own_ties(B))
    pred = W.quotient_prediction(B, H, N)
    out = {"holonomy group order": len(H), "class": cls, "lives": W.lives(Q),
           "prediction: some state constant on the orbits of N (necessary)": pred["some state constant on the orbits of N"],
           "prediction: some state fixed by H (sufficient)": pred["some state fixed by H"], "roots": []}
    nP, Pk = P
    psts = W.S.solutions(nP, Pk)
    out["pattern has ties of its own"] = any(len({s[a] ^ s[b] for s in psts}) == 1 for a in range(nP) for b in range(a + 1, nP))
    if cycle_len is not None and len(H) > 1:
        gen = [g for g in H if len(W.generated([g], m)) == len(H)]
        if gen:
            d = W.state_graph_distance(B, gen[0])
            out["state-graph distance"] = d
            out["advisor's exact condition (distance <= cycle length)"] = d is not None and d <= cycle_len
    for p in range(m):
        r = {"distinction": p}
        t = W.ties_in_copy(Q, idx, 0, p, m) if out["lives"] else None
        t0 = W.ties_in_copy(Q0, idx0, 0, p, m)
        if t is not None:
            r["tied in the copy"], r["tied outside the copy"] = t
        r["tied in the copy, untwisted"] = t0[0]
        r["predicted (quotient) tied in the copy"] = pred["ties"][p]
        out["roots"].append(r)
    return out


def block_job(i):
    import twist_lib as W
    B = BLOCKS[i]
    m = B[0]
    G = W.automorphisms(B)
    reps = [g for g in W.conjugacy_classes(G) if g != tuple(range(m))]
    rows = []
    pats = [("chain of 4 (no cycle)", W.S.chain(4), None), ("two sharing two", W.two_sharing_two(), 2),
            ("closed chain of 3", W.closed_chain(3), 3), ("closed chain of 6", W.closed_chain(6), 6)]
    for h in reps:
        for name, P, n in pats:
            r = measure(B, P, {(0, 1): h}, n)
            r.update({"twist": list(h), "pattern": name})
            rows.append(r)
        for name, P in (("ring of 6, middle twisted", W.ring(6)), ("ring of 7, middle twisted", W.ring(7))):
            tw = {(ei, 1): h for ei in range(P[0])}
            r = measure(B, P, tw, None)
            r.update({"twist": list(h), "pattern": name})
            rows.append(r)
    pairs = [(a, b) for ai, a in enumerate(reps) for b in reps[ai:]][:6]
    for a, b in pairs:
        r = measure(B, W.two_cycles(), {(0, 1): a, (3, 1): b}, None)
        r.update({"twist": [list(a), list(b)], "pattern": "two cycles of 3"})
        rows.append(r)
    return {"block": [m, [list(e) for e in B[1]]], "symmetries": len(G), "classes": len(reps), "rows": rows}


def init(bl):
    global BLOCKS
    BLOCKS = bl


def run_part(part):
    import twist_lib as W
    bl = [(m, [tuple(e) for e in E]) for m, E in W.S.blocks()]
    if part == "relation":
        return {"blocks": len(bl), "relation holds": sum(W.knot_relation_ok(B) for B in bl)}
    if part == "twists":
        el = eligible(bl)
        with Pool(12, initializer=init, initargs=(el,)) as pool:
            return {"blocks": len(el), "rows": pool.map(block_job, range(len(el)), chunksize=1)}


def summary():
    rel = json.loads((HERE / "result_relation.json").read_text())["checks"]["result"]
    tw = json.loads((HERE / "result_twists.json").read_text())["checks"]["result"]["rows"]
    cells = [(b["block"], r) for b in tw for r in b["rows"]]

    def within_changed(r):
        return r["lives"] and any(set(x.get("tied in the copy", [])) != set(x["tied in the copy, untwisted"]) for x in r["roots"])
    varies = [(blk, r["pattern"], r["twist"]) for blk, r in cells
              if r["class"] == "N-twisted" and not r["pattern has ties of its own"] and (within_changed(r) or not r["lives"])]
    single = [r for blk, r in cells if r.get("advisor's exact condition (distance <= cycle length)") is not None]
    return {
        "relation: the advisor's form holds on every block": rel["relation holds"] == rel["blocks"],
        "cells": len(cells),
        "test patterns with ties of their own (excluded from 'varies')": sorted({r["pattern"] for _, r in cells if r["pattern has ties of its own"]}),
        "classes of the cells": {c: sum(1 for _, r in cells if r["class"] == c) for c in ("balanced", "N-balanced", "N-twisted")},
        "P1 no cycle: identical to untwisted": all(r["lives"] and not within_changed(r) for blk, r in cells if r["pattern"].startswith("chain of 4")),
        "P1b balanced cells identical to untwisted": all(r["lives"] and not within_changed(r) for blk, r in cells if r["class"] == "balanced"),
        "P2 N-balanced: within-copy ties of N unchanged, lives": [sum(1 for blk, r in cells if r["class"] == "N-balanced"),
                                                                  sum(1 for blk, r in cells if r["class"] == "N-balanced" and r["lives"] and not within_changed(r))],
        "P3 N-twisted: lives with new ties inside the copy, or ends (pins that vary)": [len(varies), sum(1 for _, r in cells if r["class"] == "N-twisted")],
        "P3b N-twisted that live: measured ties contain the quotient prediction": all(set(x["predicted (quotient) tied in the copy"]) <= set(x.get("tied in the copy", [])) for blk, r in cells if r["class"] == "N-twisted" and r["lives"] for x in r["roots"]),
        "P3c measured ties equal the quotient prediction (lives)": sum(1 for blk, r in cells if r["lives"] and all(set(x["predicted (quotient) tied in the copy"]) == set(x.get("tied in the copy", [])) for x in r["roots"])),
        "living cells": sum(1 for _, r in cells if r["lives"]),
        "P4 necessary condition never violated (lives => some state constant on orbits)": all(r["prediction: some state constant on the orbits of N (necessary)"] for _, r in cells if r["lives"]),
        "P4 sufficient condition never violated (some state fixed by H => lives)": all(r["lives"] for _, r in cells if r["prediction: some state fixed by H (sufficient)"]),
        "P5 the advisor's exact condition on one cycle": [len(single), sum(1 for r in single if r["advisor's exact condition (distance <= cycle length)"] == r["lives"])],
        "P6 length dependence (cells where cycles of 3 and 6 differ)": sum(1 for b in tw for h in {json.dumps(r["twist"]) for r in b["rows"]}
            if len({r["lives"] for r in b["rows"] if json.dumps(r["twist"]) == h and r["pattern"] in ("closed chain of 3", "closed chain of 6")}) > 1),
        "P7 rings: classes of the middle twist on 6 and 7": [(r["pattern"], r["class"], r["lives"]) for blk, r in cells if r["pattern"].startswith("ring")][:40],
        "pins that vary (blocks, patterns, twists)": varies[:60],
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
        print("result reproduced" if json.dumps(old["result"], sort_keys=True, default=str) == json.dumps(json.loads(json.dumps(res["result"], default=str)), sort_keys=True) else "result differs")


if __name__ == "__main__":
    main()
