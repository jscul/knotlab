#!/usr/bin/env python3
"""Referee LIFE-JUMPS-R1, part 2: the growths regenerated with the referee's own generators (RANDOM-FATES-R1's ref_fates.py, which
draw in the frozen order) from LIFE-JUMPS's seeds (sha256 of "LJ:label:run", first 12 hex digits), checked against the records
(knots, ended, distinctions at the end, the ending knot); then, for every ending of X(0.3), X(0.35), O global (0.3) and O local
(0.3), J6 against an age-by-degree null: the largest class's size L (from the record) drawn L times without replacement from the
distinctions with probability proportional to their number of knots at the last base, 400 draws; the null's median arrival index
over the distinctions, against the record's.

    python3 -B ref_regen.py [workers]      (writes result_regen.jsonl, result_regen_summary.json)"""
import json
import random
import sys
import time
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from pysat.solvers import Glucose4

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research" / "RANDOM-FATES-20261112-001" / "referee-R1"))
import ref_fates as RF  # noqa: E402

ART = ROOT / "artifacts" / "LIFE-JUMPS-20261112-001A" / "LIFE-JUMPS-20261112-001A-E001_whole_lives"
HORIZON = {"X0.2": 6000, "X0.3": 6000, "X0.35": 2000, "Og0.3": 2000, "Ol0.3": 2000}
G4 = ("X0.3", "X0.35", "Og0.3", "Ol0.3")


def grow(label, run):
    rng = random.Random(RF.seed_of("LJ", label, run))
    horizon = 50 * int(label[1:]) if label.startswith("U") else HORIZON[label]
    g = RF.make(label, rng)
    knots = []
    with Glucose4() as s:
        for _ in range(horizon):
            t = next(g)
            if t is None:
                continue
            knots.append(t)
            for c in RF.nae_clauses(t):
                s.add_clause(c)
            if not s.solve():
                return knots, True
    return knots, False


def job(rec):
    t0 = time.time()
    knots, dead = grow(rec["label"], rec["run"])
    M = len(knots) - 1 if dead else len(knots)
    used = sorted({v for t in knots[:M] for v in t})
    out = {"label": rec["label"], "run": rec["run"], "knots match": len(knots) == rec["knots"], "ended match": dead == rec["dead"],
           "n_end match": len(used) == rec["n_end"], "killer match": (list(knots[-1]) == rec.get("killer")) if dead else None}
    if dead and rec["label"] in G4:
        last = rec["reads"][str(rec["knots"] - 1)]
        deg = defaultdict(int)
        for t in knots[:M]:
            for v in t:
                deg[v] += 1
        ids = np.array(used)
        w = np.array([deg[v] for v in used], dtype=float)
        w /= w.sum()
        L = last["largest"]
        rng = np.random.default_rng(rec["run"])
        meds = [float(np.median(rng.choice(ids, size=L, replace=False, p=w))) for _ in range(400)] if L > 1 else []
        n = len(used)
        out.update({"n_end": n, "largest": L, "record median index / n": last.get("members_median_index", float("nan")) / n,
                    "null median index / n (mean)": float(np.mean(meds)) / n if meds else None,
                    "null 5th percentile / n": float(np.quantile(meds, 0.05)) / n if meds else None,
                    "null below (n - 1) / 2": float(np.mean([m < (n - 1) / 2 for m in meds])) if meds else None})
    out["seconds"] = round(time.time() - t0, 1)
    return out


def main():
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    recs = [json.loads(l) for l in (ART / "runs.jsonl").read_text().splitlines()]
    recs = [r for r in recs if r["label"] in G4 and r["dead"]] + [r for r in recs if r["label"].startswith("U")][:40]
    path = HERE / "result_regen.jsonl"
    done = set()
    if path.exists():
        done = {(json.loads(l)["label"], json.loads(l)["run"]) for l in path.read_text().splitlines()}
    todo = [r for r in recs if (r["label"], r["run"]) not in done]
    t0 = time.time()
    with Pool(workers) as pool:
        for res in pool.imap_unordered(job, todo):
            with open(path, "a") as fh:
                fh.write(json.dumps(res) + "\n")
    rows = [json.loads(l) for l in path.read_text().splitlines()]
    summ = {"regenerated": len(rows), "all match": all(r["knots match"] and r["ended match"] and r["n_end match"] and r["killer match"] in (True, None) for r in rows)}
    for lab in G4:
        rs = [r for r in rows if r["label"] == lab and r.get("null median index / n (mean)") is not None]
        summ[lab] = {"endings": len(rs), "record median index / n (median)": float(np.median([r["record median index / n"] for r in rs])),
                     "null median index / n (median)": float(np.median([r["null median index / n (mean)"] for r in rs])),
                     "null's share of draws below (n - 1) / 2 (median over endings)": float(np.median([r["null below (n - 1) / 2"] for r in rs])),
                     "endings where the record is below the null's 5th percentile": float(np.mean([r["record median index / n"] < r["null 5th percentile / n"] for r in rs]))}
    (HERE / "result_regen_summary.json").write_text(json.dumps(summ, indent=1) + "\n")
    print(json.dumps(summ, indent=1), round(time.time() - t0), "s")


if __name__ == "__main__":
    main()
