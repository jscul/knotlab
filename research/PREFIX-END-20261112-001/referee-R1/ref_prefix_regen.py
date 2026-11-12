#!/usr/bin/env python3
"""Referee PREFIX-END-R1, part 2: the 800 growths regenerated with RANDOM-FATES-R1's generator from the census's seeds (sha256 of
"PE:X0.3:run"), checked against growths.jsonl; every base's cheap features (m/n, kappa, the largest prefix density over j >= 20, the
nine decile densities) recomputed and compared; for 60 bases (20 positives, 40 negatives, seeded choice) Pnest recomputed with the
referee's own redraw (100 resamples) and the closing hazard recomputed from exact tie classes (RANDOM-FATES-R1's Base.ties).

    python3 -B ref_prefix_regen.py [workers]      (writes result_prefix_regen.json)"""
import json
import random
import sys
from math import comb
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from pysat.solvers import Glucose4

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research" / "RANDOM-FATES-20261112-001" / "referee-R1"))
sys.path.insert(0, str(ROOT / "research" / "AGE-NEST-20261112-001" / "referee-R1"))
import ref_fates as RF  # noqa: E402
import ref_agenest as AN  # noqa: E402

ART = ROOT / "artifacts" / "PREFIX-END-20261112-001A" / "PREFIX-END-20261112-001A-E001_prefix_end"


def grow(run):
    rng = random.Random(RF.seed_of("PE", "X0.3", run))
    g = RF.make("X0.3", rng)
    K = []
    with Glucose4() as s:
        for _ in range(6000):
            t = next(g)
            if t is None:
                continue
            K.append(tuple(sorted(t)))
            for c in RF.nae_clauses(t):
                s.add_clause(c)
            if not s.solve():
                return K, True
    return K, False


def cheap(K):
    n = max(v for t in K for v in t) + 1
    e = np.cumsum(np.bincount([t[2] for t in K], minlength=n))
    D = e / np.arange(1, n + 1)
    deg = np.bincount([v for t in K for v in t], minlength=n)
    return {"mn": len(K) / n, "kappa": float((deg * (deg - 1)).sum() / deg.sum()), "maxD": float(D[19:].max()) if n > 20 else float(D.max()),
            "deciles": [float(D[max(1, int(round(n * x))) - 1]) for x in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9)]}


def hazard(K):
    n = max(v for t in K for v in t) + 1
    b = RF.Base(n, K, samples=200, seed=3)
    cls = b.ties()
    # sides: members equal to the class's first member, or not (from one state)
    tot = 0
    for c in cls:
        ref = b.R[0, c[0]]
        a = sum(1 for v in c if b.R[0, v] == ref)
        tot += comb(a, 3) + comb(len(c) - a, 3)
    b.close()
    return tot / comb(n, 3)


def job(run):
    K, dead = grow(run)
    return run, K, dead


def main():
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    G = {json.loads(l)["run"]: json.loads(l) for l in (ART / "growths.jsonl").read_text().splitlines()}
    B = [json.loads(l) for l in (ART / "bases.jsonl").read_text().splitlines()]
    with Pool(workers) as pool:
        grown = {r: (K, d) for r, K, d in pool.imap_unordered(job, range(800), chunksize=4)}
    out = {"growths": len(grown), "knots and ending match": sum(1 for r, (K, d) in grown.items() if (len(K), d) == (G[r]["knots"], G[r]["dead"]))}
    ok = tot = 0
    worst = 0.0
    for b in B:
        K = grown[b["run"]][0][:b["M"]]
        f = cheap(K)
        tot += 1
        dev = max(abs(f["mn"] - b["mn"]), abs(f["kappa"] - b["kappa"]), abs(f["maxD"] - b["maxD"]),
                  max(abs(x - y) for x, y in zip(f["deciles"], b["deciles"])))
        worst = max(worst, dev)
        ok += dev < 1e-9
    out["bases"] = tot
    out["cheap features identical"] = ok
    out["largest deviation"] = worst
    rng = random.Random(5)
    pos = [b for b in B if b["role"] == "pos"]
    negs = [b for b in B if b["role"] == "neg"]
    pick = rng.sample(pos, 20) + rng.sample(negs, 40)
    rows = []
    for b in pick:
        K = grown[b["run"]][0][:b["M"]]
        r2 = random.Random(b["run"] * 13 + b["M"])
        pn = sum(not RF_sat(AN.r2p(K, r2)) for _ in range(100)) / 100
        hz = hazard(K) if len(K) <= 2500 else None
        rows.append({"run": b["run"], "M": b["M"], "role": b["role"], "Pnest census": b["Pnest"], "Pnest referee": pn,
                     "hazard census": b["hazard"], "hazard referee": hz})
        print(rows[-1], flush=True)
    out["sample"] = rows
    pc = np.array([r["Pnest census"] for r in rows])
    pr = np.array([r["Pnest referee"] for r in rows])
    out["Pnest: mean absolute difference, correlation"] = [float(np.abs(pc - pr).mean()), float(np.corrcoef(pc, pr)[0, 1])]
    hz = [(r["hazard census"], r["hazard referee"]) for r in rows if r["hazard referee"] is not None]
    out["hazard: checked, identical to 1e-12"] = [len(hz), sum(1 for a, c in hz if abs(a - c) < 1e-12)]
    (HERE / "result_prefix_regen.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "sample"}, indent=1))


def RF_sat(K):
    from pysat.solvers import Solver
    with Solver(name="cadical153", bootstrap_with=[c for t in K for c in RF.nae_clauses(t)]) as s:
        return s.solve()


if __name__ == "__main__":
    main()
