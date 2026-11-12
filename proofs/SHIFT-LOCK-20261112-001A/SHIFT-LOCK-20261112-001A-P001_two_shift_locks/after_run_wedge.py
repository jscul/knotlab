#!/usr/bin/env python3
"""After the run (descriptive; not frozen): the shape of the lock set of the mixed-knot repeats, past the frozen range. For every harmony
with a locked cell among the frozen n, m = 2..9, whether the n x m repeat locks for n, m = 2..16 (one solver call per cell, unbounded).

    .venv/bin/python3 -B after_run_wedge.py [--write]"""
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
T0 = time.time()
NS = range(2, 17)


def job(arg):
    i, n = arg
    import shift_lib as L
    h = L.harmonies()[i]
    S = L.setup(h)
    return {"i": i, "harmony": L.name(h), "n": n,
            "locked m": [m for m in NS if L.unlocking_state(S, L.two_shift_pattern(n, m)) is None]}


def main():
    two = json.loads((HERE / "result_two.json").read_text())["checks"]["result"]["rows"]
    pick = [r["i"] for r in two if any(not x["unlocks"] for x in r["rows"])]
    with Pool(8) as pool:
        rows = pool.map(job, [(i, n) for n in reversed(NS) for i in pick], chunksize=1)
    by = {}
    for r in rows:
        by.setdefault((r["i"], r["harmony"]), {})[r["n"]] = r["locked m"]
    out = [{"i": i, "harmony": h, "locked": {str(n): v[n] for n in sorted(v)}} for (i, h), v in sorted(by.items())]
    for r in out:
        print(r["harmony"][:40])
        for n in NS:
            ms = set(r["locked"][str(n)])
            print("   n=%2d " % n + "".join("L" if m in ms else "." for m in NS))
    if "--write" in sys.argv:
        (HERE / "result_after_run_wedge.json").write_text(json.dumps({"rows": out, "seconds": round(time.time() - T0, 1)}, indent=1) + "\n")


if __name__ == "__main__":
    main()
