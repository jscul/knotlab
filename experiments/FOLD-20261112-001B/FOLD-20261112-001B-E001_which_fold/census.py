"""The frozen census of FOLD-20261112-001B-E001 (contract.json beside this file): which shortcut bases fold.

On each of the 42 bases where BOND-BALLS-20261111-001A-E001 found a shortcut (its census.json), around the origin distinction: for k = 5
and k = 6, is there a distinction w k steps away and two distinctions x, y each within one step of w such that {origin, w, x, y} is a
bond of four (constrained in the window of radius 15, every three-element part free by PERIODIC-READ's bounds)? A base folds, to six
steps, when there is one at both k. The search stops at the first bond found for each k.

Run from the repository root:
    .venv/bin/python -B experiments/FOLD-20261112-001B/FOLD-20261112-001B-E001_which_fold/census.py
Output: artifacts/FOLD-20261112-001B/FOLD-20261112-001B-E001_which_fold/census.json and census_log.txt.
"""

from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
import os
import sys
import time
from collections import Counter
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
BB = os.path.join(ROOT, "experiments", "BOND-BALLS-20261111-001A", "BOND-BALLS-20261111-001A-E001_bond_balls")
BB_SHA = "d10ec0db9055dabc0ed26f7a7174314f69c5c12d2508cff2f13231c35d2e33f1"
BB_OUT = os.path.join(ROOT, "artifacts", "BOND-BALLS-20261111-001A", "BOND-BALLS-20261111-001A-E001_bond_balls", "census.json")
OUT = os.path.join(ROOT, "artifacts", "FOLD-20261112-001B", "FOLD-20261112-001B-E001_which_fold")
R, KS, WORKERS = 15, (5, 6), 8


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


bb = load("bond_balls_census", os.path.join(BB, "census.py"))
pr = bb.pr


def log(*a):
    msg = " ".join(str(x) for x in a)
    print(msg, flush=True)
    with open(os.path.join(OUT, "census_log.txt"), "a") as f:
        f.write(msg + "\n")


def read_base(item):
    idx, knots = item
    P = pr.Pattern(2, 1, [tuple((v, tuple(s)) for v, s in kn) for kn in knots])
    rd = pr.Reader(P, R, pr.F2_LATTICES, window_exact=False, strips=pr.F2_STRIPS)
    smp = bb.Sampler(rd, bb.SEED + 1000 + idx)
    adj, _ = pr.adjacency(P, R)
    o = (0, (0, 0))
    dist = pr.ball(adj, [o], max(KS))
    cache = {}
    found = {}
    for k in KS:
        hit = None
        tried = 0
        for w in sorted(x for x, v in dist.items() if v == k):
            near = sorted(x for x in pr.ball(adj, [w], 1) if x not in (o, w))
            for x, y in itertools.combinations(near, 2):
                tried += 1
                S = tuple(sorted((o, w, x, y)))
                if not bb.refuted(rd, smp, S, cache):
                    continue
                parts = [bb.status(rd, smp, tuple(sorted(set(S) - {u})), cache) for u in S]
                if all(p == "free" for p in parts):
                    hit = [[z[0], list(z[1])] for z in S]
                    break
            if hit:
                break
        found[k] = {"bond": hit, "candidates tried": tried}
    rd.close()
    return {"index": idx, "knots": knots, "found": {str(k): v for k, v in found.items()},
            "folds": all(found[k]["bond"] for k in KS)}


def main():
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, "census_log.txt"), "w").close()
    t0 = time.time()
    have = hashlib.sha256(open(os.path.join(BB, "census.py"), "rb").read()).hexdigest()
    log("BOND-BALLS's census hash matches:", have == BB_SHA)
    if have != BB_SHA:
        raise SystemExit("BOND-BALLS's census changed")
    src = json.load(open(BB_OUT))["bases"]
    sc = [r for r in src if r["three steps"].get("bond of four (shortcut)") or r["four steps"].get("bond of four (shortcut)")]
    four = {r["index"] for r in sc if r["four steps"].get("bond of four (shortcut)")}
    log("shortcut bases:", len(sc), "with a four-step shortcut:", len(four))
    with Pool(WORKERS) as pool:
        recs = pool.map(read_base, [(r["index"], r["knots"]) for r in sc], chunksize=1)
    for r in recs:
        r["four-step shortcut"] = r["index"] in four
    folds = [r["index"] for r in recs if r["folds"]]
    g_bad = [r["index"] for r in recs if r["folds"] and not r["four-step shortcut"]]
    summary = {"bases": len(recs), "fold to six steps": folds,
               "by four-step shortcut": dict(Counter(f"four-step={r['four-step shortcut']} folds={r['folds']}" for r in recs)),
               "G": {"folding bases without a four-step shortcut": g_bad, "holds": not g_bad}}
    summary["failures"] = [] if summary["G"]["holds"] else ["G"]
    log("summary:", json.dumps(summary)[:3000])
    json.dump({"bases": recs, "summary": summary}, open(os.path.join(OUT, "census.json"), "w"), indent=1)
    log("done", round(time.time() - t0, 1), "s")


if __name__ == "__main__":
    main()
