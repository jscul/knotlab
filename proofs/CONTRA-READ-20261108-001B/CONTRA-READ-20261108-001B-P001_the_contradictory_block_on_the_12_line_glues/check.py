#!/usr/bin/env python3
"""Checks for CONTRA-READ-20261108-001B: the contradictory class's glue block on the five 12-line trisum glues.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy, networkx). Uses up to 8 processes."""
import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import hashlib  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from multiprocessing import Pool  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/CONTRA-READ-20261108-001A/CONTRA-READ-20261108-001A-P001_every_row_singles_out_the_contradictory_class"))
import contra_lib as CL  # noqa: E402

CL.TR.engine()
SEEDS = [1, 192, 240, 246, 300]
RUNS = CL.PL.SW.generate(SEEDS, 0)
GLUES = {s: CL.Glue(s, RUNS[s]) for s in SEEDS}
T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:3000], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def row_task(job):
    s, a, m = job
    return GLUES[s].row(a, m)[0]


def count_task(job):
    s, m = job
    return len(GLUES[s].solutions(m))


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(("manifest.json", "result.json")) and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved",
          not bad and all(s in ("Proved", "passed") for s in status.values()), {"mismatched": bad, "statuses": status})

    shape = {str(s): {"lines": G.g, "points": G.n, "cycle rank": len(G.off), "classes": G.N} for s, G in GLUES.items()}
    with Pool(8) as pool:
        counts = {s: pool.map(count_task, [(s, m) for m in range(GLUES[s].N)], chunksize=64) for s in SEEDS}
    pf = {s: GLUES[s].mask_of(GLUES[s].minimal) for s in SEEDS}
    unsat = {s: [m for m in range(GLUES[s].N) if counts[s][m] == 0] for s in SEEDS}
    check("1 the five 12-line glues (12 points, cycle rank 13, 8,192 classes each): on each, exactly one class has no solution, the class "
          "of the generator's Pfaffian signing",
          all(GLUES[s].g == 12 and GLUES[s].N == 8192 for s in SEEDS) and all(unsat[s] == [pf[s]] for s in SEEDS), {"glues": shape})

    logs, alone = {}, True
    with Pool(8) as pool:
        for s in SEEDS:
            G = GLUES[s]
            target = dict(enumerate(pool.map(row_task, [(s, a, pf[s]) for a in range(G.g)])))
            cand, log = list(range(G.N)), []
            for a in range(G.g):
                reps = {}
                for m in cand:
                    reps.setdefault(G.restr(a, m), m)
                rows = dict(zip(reps, pool.map(row_task, [(s, a, m) for m in reps.values()], chunksize=8)))
                cand = [m for m in cand if rows[G.restr(a, m)] == target[a]]
                log.append([len(reps), len(cand)])
            logs[str(s)] = log
            alone &= cand == [pf[s]]
    check("2 the contradictory block is its own: following, line by line, only the classes whose row equals the contradictory class's "
          "(each row computed once per class of the glue without its line), no other class survives on any of the five glues; after the "
          "first line only the four classes over the contradictory class's restriction remain",
          alone and all(v[0] == [2048, 4] for v in logs.values()),
          {"rows computed and classes left, per line": logs})

    OUT["seconds"] = round(time.time() - T0, 1)
    print("ALL OK", OUT["seconds"], "s")
    result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
              "proof": manifest["proof"], "status": "passed", "claim": manifest["claim"],
              "checks": {k: v for k, v in OUT.items() if k != "seconds"}}
    text = json.dumps(result, indent=1, sort_keys=True, default=str) + "\n"
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(text)
    elif not (HERE / "result.json").exists() or json.loads((HERE / "result.json").read_text()) != json.loads(text):
        print("result.json does not match a fresh run; rerun with --write after review")
