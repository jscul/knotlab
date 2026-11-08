#!/usr/bin/env python3
"""The exact creation map of ticket C's space (space.json) with order_lib.exact_row: ticket B's lean enumeration in one fixed point
order for every row (breadth-first from the start that keeps the fewest lines open); each row is saved in rows/ as it finishes, so a
stopped run resumes; then map.json.gz.

    python3 -B compute_map.py [workers]     (default 22)"""
import gzip
import json
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import order_lib as OL  # noqa: E402

OL.TR.engine()                                  # load the creation engine once, before the workers fork
SP = json.loads((HERE / "space.json").read_text())["space"]
H, N = [tuple(l) for l in SP["lines"]], SP["points"]
WIDTH, START, ORDER = OL.fixed_order(H, N)
ROWS = HERE / "rows"


def row(M):
    out, ns = OL.exact_row(H, N, M, ORDER)
    rec = {"row": {str(L): (None if v is None else [int(x) for x in v]) for L, v in out.items()}, "solutions": ns}
    tmp = ROWS / ("row%d.json.tmp" % M)
    tmp.write_text(json.dumps(rec))
    os.replace(tmp, ROWS / ("row%d.json" % M))
    return M


if __name__ == "__main__":
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 22
    ROWS.mkdir(exist_ok=True)
    todo = [M for M in range(len(H)) if not (ROWS / ("row%d.json" % M)).exists()]
    print("order from point", START, "keeps at most", WIDTH, "lines open;", len(todo), "rows to compute", flush=True)
    t0 = time.time()
    with Pool(workers) as pool:
        for M in pool.imap_unordered(row, todo, chunksize=1):
            print("row", M, "done", round(time.time() - t0, 1), "s", flush=True)
    rows = {str(M): json.loads((ROWS / ("row%d.json" % M)).read_text()) for M in range(len(H))}
    with gzip.open(HERE / "map.json.gz", "wt") as f:
        json.dump({"seed": SP["seed"], "lines": [list(l) for l in H], "points": N, "rows": rows}, f, sort_keys=True)
    print("map.json.gz written", round(time.time() - t0, 1), "s", flush=True)
