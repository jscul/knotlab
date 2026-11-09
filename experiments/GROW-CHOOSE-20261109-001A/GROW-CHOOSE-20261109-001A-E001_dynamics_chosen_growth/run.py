#!/usr/bin/env python3
"""Run GROW-CHOOSE-20261109-001A-E001 (frozen contract beside this file): growth chosen by the dynamics on running square tubes.

    .venv/bin/python3 -B run.py        writes artifacts/GROW-CHOOSE-20261109-001A/GROW-CHOOSE-20261109-001A-E001_dynamics_chosen_growth/run/result.json
8 worker processes, one job per (tube, split, rule)."""
import copy
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import choose_lib as C  # noqa: E402

TUBES = ((3, 3, 2), (3, 4, 2), (4, 4, 2), (3, 3, 3))
SPLITS = ("fresh", "lower", "upper", "copy")
RULES = ("all", "first, rows listed first", "first, columns listed first")
HORIZON = 12
CAP = 20000          # state steps per persistence reading; beyond it the cut is recorded as unknown
MAX_RINGS = 120      # a run whose network exceeds this many rings stops there, recorded
OUT = ROOT / "artifacts/GROW-CHOOSE-20261109-001A/GROW-CHOOSE-20261109-001A-E001_dynamics_chosen_growth/run/result.json"


def label(x):
    return x if isinstance(x, int) else "b%d.%d" % (x[1], x[2])


def one(job):
    (n, m, g), split, rule = job
    t0 = time.time()
    run = C.Run2(C.Tube2(list(range(n)), list(range(m)), g))
    lags = []
    for t in range(HORIZON + 1):
        cuts = [("row", a) for a in run.tube.rows] + [("col", a) for a in run.tube.cols]
        if rule == "first, columns listed first":
            cuts = [x for x in cuts if x[0] == "col"] + [x for x in cuts if x[0] == "row"]
        clean, unknown = [], []
        for k, (kind, a) in enumerate(cuts):
            r2 = copy.deepcopy(run)
            r2.insert(kind, a, ("b", t, k), split)
            ok = C.persists(r2, CAP)
            if ok is None:
                unknown.append((kind, label(a)))
            elif ok:
                clean.append((kind, a, k))
        entry = {"lag": t, "columns": len(run.tube.cols), "rows": len(run.tube.rows),
                 "clean cuts": [(kind, label(a)) for kind, a, k in clean], "unknown cuts": unknown}
        if clean:
            if rule == "all":
                r2 = copy.deepcopy(run)
                for kind, a, k in clean:
                    r2.insert(kind, a, ("b", t, k), split)
                ok = C.persists(r2, CAP)
                entry["all at once"] = ok
                if ok:
                    run = r2
                    entry["inserted"] = [(kind, label(a)) for kind, a, k in clean]
            else:
                kind, a, k = clean[0]
                run.insert(kind, a, ("b", t, k), split)
                entry["inserted"] = [(kind, label(a))]
        lags.append(entry)
        run.step()
        if len(run.tube.cols) * len(run.tube.rows) > MAX_RINGS:
            lags.append({"lag": t + 1, "stopped": "network of %d x %d rings exceeds %d" % (len(run.tube.cols), len(run.tube.rows), MAX_RINGS)})
            break
    res = {"tube": "%d x %d, g = %d" % (n, m, g), "split": split, "rule": rule, "lags": lags,
           "final": [len(run.tube.cols), len(run.tube.rows)], "seconds": round(time.time() - t0, 1)}
    part = OUT.parent / ("job %d x %d g%d %s %s.json" % (n, m, g, split, rule.replace(",", "")))
    part.parent.mkdir(parents=True, exist_ok=True)
    part.write_text(json.dumps(res, indent=1) + "\n")
    print(res["tube"], res["split"], res["rule"], "final", res["final"], res["seconds"], "s", flush=True)
    return res


def main():
    jobs = [(tb, s, r) for tb in TUBES for s in SPLITS for r in RULES]
    with Pool(8) as pool:
        res = pool.map(one, jobs, chunksize=1)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"experiment_id": "GROW-CHOOSE-20261109-001A-E001", "horizon": HORIZON, "runs": res}, indent=1) + "\n")
    for r in res:
        grown = [e["lag"] for e in r["lags"] if e.get("inserted")]
        dirs = sorted({k for e in r["lags"] for k, a in e.get("inserted", [])})
        print(r["tube"], r["split"], r["rule"], "final", r["final"], "lags with growth", grown, "directions", dirs,
              "unknown", sum(len(e.get("unknown cuts", [])) for e in r["lags"]), r["seconds"], "s")


if __name__ == "__main__":
    main()
