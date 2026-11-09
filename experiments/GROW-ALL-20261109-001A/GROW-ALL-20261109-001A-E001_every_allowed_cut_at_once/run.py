#!/usr/bin/env python3
"""Run GROW-ALL-20261109-001A-E001 (frozen contract beside this file): growth by every allowed cut at once, past lag 1.

    .venv/bin/python3 -B run.py
On GROW-CHOOSE-20261109-001A-E001's choose_lib (persistence read by iterating the state to a repeat, Brent's method). At each lag every
cut (after each row label and after each column label) is read on a copy of the run, 8 worker processes over the cuts; every allowed
cut then gets a band at once, the combination is read, and the run steps. A run stops at the first lag with no allowed cut, at lag 3,
or when the next network would pass MAX_RINGS. Each tube's record is written as soon as it is done, to
artifacts/GROW-ALL-20261109-001A/GROW-ALL-20261109-001A-E001_every_allowed_cut_at_once/run/."""
import copy
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "experiments/GROW-CHOOSE-20261109-001A/GROW-CHOOSE-20261109-001A-E001_dynamics_chosen_growth"))
import choose_lib as C  # noqa: E402

TUBES = ((4, 4, 2), (3, 4, 2), (3, 3, 3), (3, 3, 2))
SPLIT = "fresh"
LAST_LAG = 3
CAP = 400000
CAP_LAG3 = 50000     # lag 3: a failure is read exactly; no failure within 50,000 steps is recorded as unknown
MAX_RINGS = 700
OUTDIR = ROOT / "artifacts/GROW-ALL-20261109-001A/GROW-ALL-20261109-001A-E001_every_allowed_cut_at_once/run"


def label(x):
    return x if isinstance(x, int) else "b%d.%d" % (x[1], x[2])


def read_cut(job):
    run, kind, a, t, k = job
    r2 = copy.deepcopy(run)
    r2.insert(kind, a, ("b", t, k), SPLIT)
    t0 = time.time()
    return kind, a, k, C.persists(r2, CAP if t < 3 else CAP_LAG3), round(time.time() - t0, 1)


def tube(n, m, g, pool):
    run = C.Run2(C.Tube2(list(range(n)), list(range(m)), g))
    lags = []
    for t in range(LAST_LAG + 1):
        cuts = [("row", a) for a in run.tube.rows] + [("col", a) for a in run.tube.cols]
        res = pool.map(read_cut, [(run, kind, a, t, k) for k, (kind, a) in enumerate(cuts)], chunksize=1)
        allowed = [(kind, a, k) for kind, a, k, ok, s in res if ok is True]
        entry = {"lag": t, "columns": len(run.tube.cols), "rows": len(run.tube.rows), "cuts": len(cuts),
                 "allowed": [(kind, label(a)) for kind, a, k in allowed],
                 "refused": [(kind, label(a)) for kind, a, k, ok, s in res if ok is False],
                 "unknown": [(kind, label(a)) for kind, a, k, ok, s in res if ok is None],
                 "slowest reading, seconds": max(s for *_, s in res)}
        lags.append(entry)
        print(n, m, g, "lag", t, "%d x %d" % (entry["columns"], entry["rows"]), "allowed", len(entry["allowed"]), "refused",
              len(entry["refused"]), "unknown", len(entry["unknown"]), flush=True)
        if not allowed:
            break
        cols = len(run.tube.cols) + sum(1 for kind, a, k in allowed if kind == "col")
        rows = len(run.tube.rows) + sum(1 for kind, a, k in allowed if kind == "row")
        if cols * rows > MAX_RINGS:
            entry["stopped"] = "the next network, %d x %d rings, would pass %d" % (cols, rows, MAX_RINGS)
            break
        if t == LAST_LAG:
            break
        for kind, a, k in allowed:
            run.insert(kind, a, ("b", t, k), SPLIT)
        entry["combination persists"] = C.persists(run, CAP)
        print(n, m, g, "lag", t, "combination persists:", entry["combination persists"], flush=True)
        if entry["combination persists"] is not True:
            break
        run.step()
    rec = {"tube": "%d x %d, g = %d" % (n, m, g), "split": SPLIT, "lags": lags}
    OUTDIR.mkdir(parents=True, exist_ok=True)
    (OUTDIR / ("tube_%dx%d_g%d.json" % (n, m, g))).write_text(json.dumps(rec, indent=1) + "\n")
    return rec


def main():
    t0 = time.time()
    with Pool(8) as pool:
        recs = [tube(n, m, g, pool) for n, m, g in TUBES]
    (OUTDIR / "result.json").write_text(json.dumps({"experiment_id": "GROW-ALL-20261109-001A-E001", "runs": recs,
                                                    "seconds": round(time.time() - t0)}, indent=1) + "\n")
    for p in OUTDIR.glob("tube_*.json"):
        p.unlink()
    print("done", round(time.time() - t0), "s")


if __name__ == "__main__":
    main()
