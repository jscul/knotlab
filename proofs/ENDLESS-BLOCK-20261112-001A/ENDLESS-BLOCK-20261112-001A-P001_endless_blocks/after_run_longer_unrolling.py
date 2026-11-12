#!/usr/bin/env python3
"""After the run, descriptive (not frozen): are the one-order cycle-born ties an artefact of the finite unrolling? For every harmony and
closed chain with cycle-born ties in result_one.json, unroll the closed chain nine times instead of three (root in the middle, four
copies of the chain on each side) and test whether each cycle-born tie is still absent there for both lifts of its far end.

    .venv/bin/python3 -B after_run_longer_unrolling.py"""
import json
import sys
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import endless_lib as E  # noqa: E402


def job(arg):
    n, pattern, born = arg
    h = E.harmonies()[n]
    k = int(pattern.split()[-1])
    U = E.open_chain(9 * k)
    cl, nv, var = E.build(U, h, "one order")
    mid = 8 * k  # copy index of the middle shared distinction (an even index, 4 chain lengths from each end)
    still, gone = 0, 0
    cache = {}
    for (i, v, j, r) in born:
        if i not in cache:
            cache[i] = E.tie_set(cl, nv, var(mid, i))
        tt = cache[i]
        if any(var(L, j) in tt for L in (mid + v, mid + v - 2 * k)):
            gone += 1
        else:
            still += 1
    return {"harmony": h["orbits"], "pattern": pattern, "cycle-born ties": len(born), "still untied on the long unrolling": still,
            "tied there (an artefact)": gone}


if __name__ == "__main__":
    on = json.loads((HERE / "result_one.json").read_text())["checks"]["result"]["rows"]
    jobs = [(hn, r["pattern"], r["cycle-born ties (closed chain vs unrolled chain)"]) for hn, h in enumerate(on) for r in h["rows"]
            if r.get("cycle-born ties (closed chain vs unrolled chain)")]
    with Pool(12) as pool:
        rows = pool.map(job, jobs, chunksize=1)
    out = {"status": "descriptive, after the run", "rows": rows,
           "cycle-born ties": sum(r["cycle-born ties"] for r in rows), "still cycle-born": sum(r["still untied on the long unrolling"] for r in rows)}
    (HERE / "result_after_run_longer_unrolling.json").write_text(json.dumps(out, indent=1) + "\n")
    print({k: v for k, v in out.items() if k != "rows"}, len(rows), "cells")
