#!/usr/bin/env python3
"""Exact native creation maps of the alternative placements listed as mapped in placements.json, regenerated under their hash seeds
and computed with TRISUM-READ C's fixed-order enumerator; one file per placement in map_cache/, then maps.json.gz.

    python3 -B compute_maps.py [workers]     (default 20)"""
import gzip
import json
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import sw_lib as SW  # noqa: E402
sys.path.insert(0, str(SW.TRC))
import order_lib as OL  # noqa: E402

OL.TR.engine()
CACHE = HERE / "map_cache"
JOB = {}


def row(M):
    H, N, order = JOB["H"], JOB["N"], JOB["order"]
    out, ns = OL.exact_row(H, N, M, order)
    return M, {str(L): (None if v is None else [int(x) for x in v]) for L, v in out.items()}, ns


if __name__ == "__main__":
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    P = json.loads((HERE / "placements.json").read_text())
    CACHE.mkdir(exist_ok=True)
    for s, rec in sorted(P.items(), key=lambda kv: int(kv[0])):
        for hs in rec["mapped"]:
            path = CACHE / ("seed%s_hs%d.json.gz" % (s, hs))
            if path.exists():
                continue
            H = [tuple(l) for l in SW.generate([int(s)], hs)[int(s)]["lines"]]
            N = 1 + max(max(l) for l in H)
            JOB.update(H=H, N=N, order=OL.fixed_order(H, N)[2])
            t0 = time.time()
            with Pool(workers) as pool:
                rows = {str(M): {"row": out, "solutions": ns} for M, out, ns in pool.imap_unordered(row, range(len(H)), chunksize=1)}
            with gzip.open(str(path) + ".tmp", "wt") as f:
                json.dump({"seed": int(s), "hash seed": hs, "lines": [list(l) for l in H], "points": N, "rows": rows}, f, sort_keys=True)
            os.replace(str(path) + ".tmp", path)
            print("seed", s, "hash seed", hs, "done", round(time.time() - t0, 1), "s", flush=True)
    maps = {"%s/%d" % (s, hs): json.load(gzip.open(CACHE / ("seed%s_hs%d.json.gz" % (s, hs)), "rt"))
            for s, rec in P.items() for hs in rec["mapped"]}
    with gzip.open(HERE / "maps.json.gz", "wt") as f:
        json.dump(maps, f, sort_keys=True)
    print("maps.json.gz:", len(maps), "placements")
